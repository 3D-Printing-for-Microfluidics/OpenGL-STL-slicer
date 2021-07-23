base = [15, 10, 0.01];
top = [2, 1, 0.01];


hull() {
    cube(base);
    translate([1, 1, 5]) cube(top);
}

//hull() {
//cube(base);
//color("blue") translate([(base[0]-top[0])/2, (base[1]-top[1])/2, 5]) cube(top);
//}
