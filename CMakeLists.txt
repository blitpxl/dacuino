cmake_minimum_required(VERSION 3.10)
project(dacuino)

set(CMAKE_BUILD_TYPE "debug")
set(CMAKE_C_STANDARD 23)
set(CMAKE_C_FLAGS_DEBUG "-Wall -g -Og")

add_library(bass SHARED IMPORTED)
set_target_properties(bass PROPERTIES IMPORTED_LOCATION "${CMAKE_SOURCE_DIR}/lib/libbass.so")

add_executable(dacuino src/main.c)
target_include_directories(dacuino PRIVATE headers)
target_link_libraries(dacuino PRIVATE bass)