#ifndef PRINTER_H
#define PRINTER_H

struct Resolution
{
    Resolution(const unsigned int x, const unsigned int y) : x(x), y(y) {}
    const unsigned int x, y;
};

Resolution printer_resolution(500, 500);
const GLfloat pixel = 0.05; // pixel pitch (um)

#endif
