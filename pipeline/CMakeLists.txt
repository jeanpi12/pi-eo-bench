cmake_minimum_required(VERSION 3.25)
project(pi_eo_pipeline LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(pipeline src/main.cpp)
target_compile_options(pipeline PRIVATE -Wall -Wextra -Wpedantic)
