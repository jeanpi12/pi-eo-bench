#include <cstdint>
#include <iostream>

int main() {
    std::uint16_t pixel = 14;
    std::uint16_t dark = 15;
    std::uint16_t result = pixel - dark;

    std::cout << "pixel - dark as uint16_t: " << result << '\n';
    return 0;
}
