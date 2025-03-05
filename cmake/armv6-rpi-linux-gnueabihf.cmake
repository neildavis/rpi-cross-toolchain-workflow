# https://cmake.org/cmake/help/book/mastering-cmake/chapter/Cross%20Compiling%20With%20CMake.html

# Cross-compilation system information
set(RPI_GCC_TRIPLE "armv6-rpi-linux-gnueabihf")
# Architecture
set(CMAKE_LIBRARY_ARCHITECTURE arm-linux-gnueabihf)
set(CPACK_DEBIAN_PACKAGE_ARCHITECTURE armhf)
# Set the architecture-specific compiler flags
set(ARCH_FLAGS "-mcpu=arm1176jzf-s")
set(CMAKE_THREAD_LIBS_INIT "-lpthread -lc")

# Common ARM config
include("${CMAKE_CURRENT_LIST_DIR}/arm-common-linux.cmake")