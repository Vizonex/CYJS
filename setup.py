
from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext
import os
from pathlib import Path
import sys

use_system_lib = bool(int(os.environ.get("QUICKJS_USE_SYSTEM_LIB", 0)))

PARENT_DIR = Path(__file__).parent
QUICKJS_DIR = PARENT_DIR / "quickjs"

quickjs_sources = [
    QUICKJS_DIR / "cutils.c",
    QUICKJS_DIR / "dtoa.c",
    QUICKJS_DIR / "libregexp.c",
    QUICKJS_DIR / "libunicode.c",
    QUICKJS_DIR / "quickjs.c"
]

class quickjs_build_ext(build_ext):
    quickjs_dir = os.path.join("deps", "c-ares")
    build_config_dir = os.path.join("deps", "build-config")
    ext_headers = os.path.join("quickjs")

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
        self.add_include_dir(self.ext_headers)
        c = self.compiler
        
        if not os.path.exists("build"):
                os.mkdir("build")
        sources = list(map(str, quickjs_sources))

        objects = c.compile(sources, "build")
        c.create_static_lib(objects, output_libname="cares", output_dir="build")
        
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
                import Cython
            except ImportError:
                raise RuntimeError(
                    "please install cython to compile cyjs from source"
                )

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
            Extension(
                "cyjs.cyjs",
                ["cyjs/cyjs.pyx"],
                # extra_compile_args=["-O2"]
            ),
            Extension(
                "cyjs.context",
                ["cyjs/context.pyx"],
            ),
            Extension(
                "cyjs.mem",
                ["cyjs/mem.pyx"],
            ),
            Extension(
                "cyjs.runtime",
                ["cyjs/runtime.pyx"]
            ),
            Extension(
                "cyjs.value",
                ["cyjs/value.pyx"]
            )
        ],
        cmdclass={"build_ext": quickjs_build_ext},
    )
