# https://cmake.org/cmake/help/book/mastering-cmake/chapter/Cross%20Compiling%20With%20CMake.html

# Cross-compilation system information
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR arm)

# The sysroot contains all the libraries we might need to link against and 
# possibly headers we need for compilation
set(CMAKE_SYSROOT $ENV{HOME}/x-tools/${RPI_GCC_TRIPLE}/sysroot)
set(CMAKE_FIND_ROOT_PATH ${CMAKE_SYSROOT})
set(CMAKE_STAGING_PREFIX $ENV{HOME}/.local/opt/staging/${RPI_GCC_TRIPLE})

# Set the compilers for C, C++ and Fortran
set(RPI_XTOOLS_BIN $ENV{HOME}/x-tools/${RPI_GCC_TRIPLE}/bin)
set(CMAKE_C_COMPILER ${RPI_XTOOLS_BIN}/${RPI_GCC_TRIPLE}-gcc CACHE FILEPATH "C compiler")
set(CMAKE_CXX_COMPILER ${RPI_XTOOLS_BIN}/${RPI_GCC_TRIPLE}-g++ CACHE FILEPATH "C++ compiler")
set(CMAKE_Fortran_COMPILER ${RPI_XTOOLS_BIN}/${RPI_GCC_TRIPLE}-gfortran CACHE FILEPATH "Fortran compiler")

# Set the architecture-specific compiler flags
set(CMAKE_C_FLAGS_INIT ${ARCH_FLAGS})
set(CMAKE_CXX_FLAGS_INIT ${ARCH_FLAGS})
set(CMAKE_Fortran_FLAGS_INIT ${ARCH_FLAGS})

# Don't look for programs in the sysroot (these are ARM programs, they won't run
# on the build machine)
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
# Only look for libraries, headers and packages in the sysroot, don't look on 
# the build machine
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

set(CMAKE_HAVE_THREADS_LIBRARY 1)
set(CMAKE_USE_WIN32_THREADS_INIT 0)
set(CMAKE_USE_PTHREADS_INIT 1)

set(CPACK_DEBIAN_PACKAGE_ARCHITECTURE armhf)