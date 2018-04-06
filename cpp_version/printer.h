#ifndef PRINTER_H
#define PRINTER_H

struct Resolution
{
    Resolution(const unsigned int x, const unsigned int y) : x(x), y(y) {}
    const unsigned int x, y;
};

Resolution printer_resolution(2560, 1600);
const GLfloat pixel = 0.0076; // pixel pitch (um)

#endif
