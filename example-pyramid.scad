cube_thickness = 0.01;
base = [15, 10, cube_thickness];
top = [2, 1, cube_thickness];

pyramid_height = 5;
shift_top_x = 3;
shift_top_y = 2;

hull() {
    cube(base);
    translate([shift_top_x, 
               shift_top_y, 
               pyramid_height - cube_thickness
              ]) cube(top);
}
