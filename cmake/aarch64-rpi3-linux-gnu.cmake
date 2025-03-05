# https://cmake.org/cmake/help/book/mastering-cmake/chapter/Cross%20Compiling%20With%20CMake.html

# Cross-compilation system information
set(RPI_GCC_TRIPLE "aarch64-rpi3-linux-gnu")
# Architecture
set(CMAKE_LIBRARY_ARCHITECTURE aarch64-linux-gnu)
set(CPACK_DEBIAN_PACKAGE_ARCHITECTURE arm64)
# Set the architecture-specific compiler flags
set(ARCH_FLAGS "-mcpu=cortex-a53")
set(CMAKE_THREAD_LIBS_INIT "-lpthread")

# Common ARM config
include("${CMAKE_CURRENT_LIST_DIR}/arm-common-linux.cmake")