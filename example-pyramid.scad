pedestal = [15, 10, 2];
top_thickness = 0.01;
top = [2, 1, top_thickness];

pyramid_height = 5;
shift_top_x = 3;
shift_top_y = 2;

hull() {
    cube(pedestal);
    translate([shift_top_x, 
               shift_top_y, 
               pyramid_height - top_thickness
              ]) cube(top);
}
