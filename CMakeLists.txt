cmake_minimum_required(VERSION 4.1)
project(emulator)

set(CMAKE_C_STANDARD 11)

add_executable(emulator main.c)
add_subdirectory(raylib)
target_link_libraries(emulator raylib)

add_custom_target(copy_assets
    COMMAND ${CMAKE_COMMAND} -P ${CMAKE_CURRENT_LIST_DIR}/copy_assets.cmake
)
add_dependencies(emulator copy_assets)

file(COPY z_binaries DESTINATION ${CMAKE_BINARY_DIR})
