#ifndef UTIL_H
#define UTIL_H

#include <vector>
#include "vertex.h"

std::vector<GLfloat> find_min_max(std::vector<Vertex>& vertices)
{
    GLfloat xmin = vertices[0].x;
    GLfloat xmax = vertices[0].x;
    GLfloat ymin = vertices[0].y;
    GLfloat ymax = vertices[0].y;
    GLfloat zmin = vertices[0].z;
    GLfloat zmax = vertices[0].z;
    for(int i=1; i<vertices.size(); ++i)
    {
        if(vertices[i].x < xmin)
        {
            xmin = vertices[i].x;
        }
        if(vertices[i].x > xmax) 
        {
            xmax = vertices[i].x;
        }
        
        if(vertices[i].y < ymin)
        {
            ymin = vertices[i].y;
        }
        if(vertices[i].y > ymax) 
        {
            ymax = vertices[i].y;
        }
        
        if(vertices[i].z < zmin)
        {
            zmin = vertices[i].z;
        }
        if(vertices[i].z > zmax) 
        {
            zmax = vertices[i].z;
        }
    }
    
    std::vector<GLfloat> a = {xmin, xmax, ymin, ymax, zmin, zmax};
    return a;
}

#endif
