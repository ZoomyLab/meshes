DefineConstant[ size_factor = {1, Name "size_factor"} ];
scale = 0.125 / size_factor;

length = 4.;
width =  2.;
x_hole = length/8;
y_hole = width/2;
r_hole = 0.2;
d_hole = r_hole / Sqrt(2);
height_water = 0.5;
height_air = 0.5;
N_layers = Round(30 * size_factor);
N_layers_water = N_layers * height_water/(height_air + height_water);
N_layers_air = N_layers * height_air/(height_air + height_water);

Point(1) = {0, 0, 0, scale};
Point(2) = {0, width, 0, scale};
Point(3) = {length, width, 0, scale};
Point(4) = {length, 0, 0, scale};
Point(5) = {x_hole-r_hole, y_hole, 0, scale};
Point(6) = {x_hole, y_hole+r_hole, 0, scale};
Point(7) = {x_hole+r_hole, y_hole, 0, scale};
Point(8) = {x_hole, y_hole-r_hole, 0, scale};
Point(9) = {x_hole, y_hole, 0, scale};

Line(11) = {1, 2};
Line(12) = {2, 3};
Line(13) = {3, 4};
Line(14) = {4, 1};
Circle(15) = {5, 9, 6};
Circle(16) = {6, 9, 7};
Circle(17) = {7, 9, 8};
Circle(18) = {8, 9, 5};

Curve Loop(101) = {11,12,13,14};
Curve Loop(102) = {15, 16, 17, 18};
Surface(1001) = {101, -102};

Extrude {0, 0, height_water} {
  Surface{1001}; Layers{N_layers_water}; Recombine;
}

Extrude {0, 0, height_air} {
  Surface{1043}; Layers{N_layers_air}; Recombine;
}

Physical Surface("inflow_water", 3000) = {1014};
Physical Surface("inflow_air", 3001) = {1056};
Physical Surface("top", 3002) = {1085};
Physical Surface("bottom", 3003) = {1001};
Physical Surface("front_wall", 3004) = {1068, 1026};
Physical Surface("back_wall", 3005) = {1018, 1060};
Physical Surface("outflow", 3006) = {1064, 1022};
Physical Surface("pillar", 3007) = {1084, 1042, 1072, 1030, 1080, 1038, 1076, 1034};
Physical Volume("volume", 4000) = {1, 2};
