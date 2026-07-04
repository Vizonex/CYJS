import os
import shutil
import subprocess
import sys

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext

use_system_lib = bool(int(os.environ.get("QUICKJS_USE_SYSTEM_LIB", 0)))


class quickjs_build_ext(build_ext):
    # Brought over from winloop since these can be very useful.

    user_options = build_ext.user_options + [
        ("cython-always", None, "run cythonize() even if .c files are present"),
        (
            "cython-annotate",
            None,
            "Produce a colorized HTML version of the Cython source.",
        ),
        ("cython-directives=", None, "Cythion compiler directives"),
    ]

    def initialize_options(self):
        self.cython_always = False
        self.cython_annotate = False
        self.cython_directives = None
        self.parallel = True
        super().initialize_options()

    def add_include_dir(self, dir, force=False):
        if use_system_lib and not force:
            return
        dirs = self.compiler.include_dirs
        dirs.insert(0, dir)
        self.compiler.set_include_dirs(dirs)

    def build_extensions(self):
        if use_system_lib:
            self.compiler.add_library("quickjs-ng")
            build_ext.build_extensions(self)
            return

        cmake_cmd = shutil.which("cmake")

        if not cmake_cmd:
            raise RuntimeError("cyjs requires cmake")
        quickjs_ng_vendor = os.path.join("quickjs")
        build_temp = os.path.abspath(os.path.join(self.build_temp, "qjs-build"))
        install_dir = os.path.abspath(os.path.join(self.build_temp, "qjs-install"))
        os.makedirs(build_temp, exist_ok=True)
        os.makedirs(install_dir, exist_ok=True)

        cmake_args = [
            "-DCMAKE_BUILD_TYPE=Release",
            "-DCMAKE_CONFIGURATION_TYPES=Release",
            f"-DCMAKE_INSTALL_PREFIX={install_dir}",
            "-DQJS_BUILD_LIBC=ON",  # We do need LIBC there are plans to implement it's things
            "-DQJS_BUILD_CLI=OFF",  # We don't need CLI it wastes time to make it.
            "-DBUILD_SHARED_LIBS=false",
        ]


        print(f"Configuring quickjs-ng with CMake in {build_temp}")
        subprocess.check_call(
            [cmake_cmd, os.path.abspath(quickjs_ng_vendor), *cmake_args], cwd=build_temp
        )

        print("Building quickjs-ng...")
        build_args = ["--build", ".", "--config", "Release"]

        subprocess.check_call([cmake_cmd, *build_args], cwd=build_temp)

        install_args = ["--install", ".", "--config", "Release"]
        subprocess.check_call([cmake_cmd, *install_args], cwd=build_temp)

        if sys.platform == "win32":
            # Windows libraries
            possible_paths = [
                os.path.join(install_dir, "lib", "qjs.lib"),
                os.path.join(install_dir, "lib", "qjs_static.lib"),
                os.path.join(install_dir, "lib", "libqjs.a"),  # MinGW
            ]
        else:
            possible_paths = [
                os.path.join(install_dir, "lib", "libqjs.a"),
                os.path.join(install_dir, "lib64", "libqjs.a"),
            ]

        lib_path = None
        for path in possible_paths:
            if os.path.exists(path):
                lib_path = path
                break

        # print("==== DEBUG ====")
        # print(lib_path)

        if not lib_path:
            raise RuntimeError(
                f"Could not find installed cyjs library in {install_dir}.\n"
                f"Checked: {', '.join(possible_paths)}"
            )

        self.extensions[0].extra_objects = [lib_path]

        self.add_include_dir(os.path.join(install_dir, "include"))
        self.add_include_dir(quickjs_ng_vendor)

        build_ext.build_extensions(self)

    # Copied from winloop
    def finalize_options(self):
        need_cythonize = self.cython_always
        cfiles = {}

        for extension in self.distribution.ext_modules:
            for i, sfile in enumerate(extension.sources):
                if sfile.endswith(".pyx"):
                    prefix, _ = os.path.splitext(sfile)
                    cfile = prefix + ".c"

                    if os.path.exists(cfile) and not self.cython_always:
                        extension.sources[i] = cfile
                    else:
                        if os.path.exists(cfile):
                            cfiles[cfile] = os.path.getmtime(cfile)
                        else:
                            cfiles[cfile] = 0
                        need_cythonize = True

        # from winloop & cyares
        if need_cythonize:
            # import pkg_resources

            # Double check Cython presence in case setup_requires
            # didn't go into effect (most likely because someone
            # imported Cython before setup_requires injected the
            # correct egg into sys.path.
            try:
                import Cython  # type: ignore  # noqa: F401
            except ImportError:
                raise RuntimeError("please install cython to compile cyjs from source")

            from Cython.Build import cythonize

            directives = {}
            if self.cython_directives:
                for directive in self.cython_directives.split(","):
                    k, _, v = directive.partition("=")
                    if v.lower() == "false":
                        v = False
                    if v.lower() == "true":
                        v = True
                    directives[k] = v
                self.cython_directives = directives

            self.distribution.ext_modules[:] = cythonize(
                self.distribution.ext_modules,
                compiler_directives=directives,
                annotate=self.cython_annotate,
                emit_linenums=self.debug,
                # Try using a cache to help with compiling as well...
                cache=True,
            )

        return super().finalize_options()


if __name__ == "__main__":
    setup(
        ext_modules=[
            Extension("cyjs._cyjs", ["cyjs/_cyjs.pyx"], extra_compile_args=["-fPIC"] if sys.platform == "linux" else []),
        ],
        cmdclass={"build_ext": quickjs_build_ext},
    )
