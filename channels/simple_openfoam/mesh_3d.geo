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

Line(11) = {1, 2};
Line(12) = {2, 3};
Line(13) = {3, 4};
Line(14) = {4, 1};

Curve Loop(101) = {11,12,13,14};
Surface(1001) = {101};

Extrude {0, 0, height_water} {
  Surface{1001}; Layers{N_layers_water}; Recombine;
}

Extrude {0, 0, height_air} {
  Surface{1023}; Layers{N_layers_air}; Recombine;
}

Physical Surface("inflow_water", 3000) = {1010};
Physical Surface("inflow_air", 3001) = {1032};
Physical Surface("top", 3002) = {1045};
Physical Surface("bottom", 3003) = {1001};
Physical Surface("front_wall", 3004) = {1022, 1044};
Physical Surface("back_wall", 3005) = {1014, 1036};
Physical Surface("outflow", 3006) = {1018, 1040};
Physical Volume("volume", 4000) = {1, 2};
