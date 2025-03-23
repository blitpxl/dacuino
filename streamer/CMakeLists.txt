cmake_minimum_required(VERSION 3.10)
project(decoder)

set(CMAKE_BUILD_TYPE "debug")
set(CMAKE_C_STANDARD 23)
set(CMAKE_C_FLAGS_DEBUG "-Wall -g -Og")

add_library(bass SHARED IMPORTED)
add_library(bassmix SHARED IMPORTED)
set_target_properties(bass PROPERTIES IMPORTED_LOCATION "${CMAKE_SOURCE_DIR}/lib/libbass.so")
set_target_properties(bassmix PROPERTIES IMPORTED_LOCATION "${CMAKE_SOURCE_DIR}/lib/libbassmix.so")

add_executable(decoder decoder.c)
target_include_directories(decoder PRIVATE headers)
target_link_libraries(decoder PRIVATE bass bassmix)