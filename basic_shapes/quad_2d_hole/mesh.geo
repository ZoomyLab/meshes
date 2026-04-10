DefineConstant[ size_factor = {1, Name "size_factor"} ];
cl = 1.0 / size_factor;

Point(1) = {0, 0, 0, cl};
Point(2) = {1, 0, 0, cl};
Point(3) = {1, 1, 0, cl};
Point(4) = {0, 1, 0, cl};

Line(1) = {1, 2};
Line(2) = {2, 3};
Line(3) = {3, 4};
Line(4) = {4, 1};


Point(5) = {0.4, 0.4, 0, cl};
Point(6) = {0.6, 0.4, 0, cl};
Point(7) = {0.6, 0.6, 0, cl};
Point(8) = {0.4, 0.6, 0, cl};
Point(9) = {0.5, 0.5, 0, cl};

Circle(5) = {5, 9, 6};
Circle(6) = {6, 9, 7};
Circle(7) = {7, 9, 8};
Circle(8) = {8, 9, 5};

Line(10) = {1, 5};
Line(11) = {2, 6};
Line(12) = {3, 7};
Line(13) = {4, 8};

Curve Loop(5) = {1,2,3,4};
Curve Loop(6) = {8,7,6,5};
Surface(1) = {5,6};

Physical Curve("right", 1000) = {2};
Physical Curve("left", 1001) = {4};
Physical Curve("top", 1002) = {3};
Physical Curve("bottom", 1003) = {1};
Physical Curve("hole", 1004) = {5,6,7,8};
Physical Surface("surface", 2000) = {1};
