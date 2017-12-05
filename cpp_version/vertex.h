#ifndef VERTEX_H
#define VERTEX_H

#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <boost/algorithm/string.hpp>

using namespace boost::algorithm;

struct Vertex
{
    Vertex() {}
    Vertex(GLfloat x, GLfloat y, GLfloat z) : x(x), y(y), z(z) {}
    Vertex(std::vector<GLfloat> v) : x(v[0]), y(v[1]), z(v[2]) {}

    GLfloat x, y, z;
};

// TODO - implement Normal by inheriting from Vertex
struct Normal
{
    Normal() {}
    Normal(GLfloat x, GLfloat y, GLfloat z) : x(x), y(y), z(z) {}
    Normal(std::vector<GLfloat> v) : x(v[0]), y(v[1]), z(v[2]) {}

    GLfloat x, y, z;
};

void getVertices(std::vector<Vertex>* vertices, std::vector<Normal>* normals, const std::string stl)
{
    // read ascii stl file and load all vertices into `verts`
    std::ifstream infile(stl);
    std::string line;
    while (std::getline(infile, line))
    {
        std::string trimmed_string = trim_copy(line);
        
        if(starts_with(trimmed_string, "vertex"))
        {
            std::stringstream stream(trimmed_string.substr(6, trimmed_string.size()));
            std::vector<GLfloat> values(
                 (std::istream_iterator<GLfloat>(stream)),
                 (std::istream_iterator<GLfloat>()));
                 
            Vertex vert(values);
            vertices->push_back(vert);
        } else if (starts_with(trimmed_string, "facet"))
        {
            std::stringstream stream(trimmed_string.substr(12, trimmed_string.size()));
            std::vector<GLfloat> values(
                 (std::istream_iterator<GLfloat>(stream)),
                 (std::istream_iterator<GLfloat>()));
                 
            Normal norm(values);
            normals->push_back(norm);
            normals->push_back(norm);
            normals->push_back(norm);
        }
    }
}

#endif
