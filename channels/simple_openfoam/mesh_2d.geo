DefineConstant[ size_factor = {1, Name "size_factor"} ];
scale = 0.125 / size_factor;

length = 4.;
width =  2.;
x_hole = length/8;
y_hole = width/2;
r_hole = 0.2;
d_hole = r_hole / Sqrt(2);
height_water = 0.8;
height_air = 0.2;
N_layers = 30;
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

Physical Curve("inflow", 3000) = {11};
Physical Curve("top", 3001) = {12};
Physical Curve("outflow", 3002) = {13};
Physical Curve("bottom", 3003) = {14};
Physical Surface("volume", 4000) = {1001};
