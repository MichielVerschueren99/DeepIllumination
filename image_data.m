
MSE = 0;
for x = 0:9
    result = imread(sprintf('result\\sphere_in_cornell\\%d.png', x));
    gt = imread(sprintf('dataset\\sphere_in_cornell\\test\\gt\\%d.png', x));
    MSE = MSE + immse(gt, result);
end
mean_MSE_normal = MSE / 10

MSE = 0;
for x = 0:9
    result = imread(sprintf('result\\sphere_in_cornell_no_normal\\%d.png', x));
    gt = imread(sprintf('dataset\\sphere_in_cornell_no_normal\\test\\gt\\%d.png', x));
    MSE = MSE + immse(gt, result);
end
mean_MSE_no_normal = MSE / 10

MSE = 0;
for x = 0:9
    result = imread(sprintf('result\\sphere_in_cornell_no_depth\\%d.png', x));
    gt = imread(sprintf('dataset\\sphere_in_cornell_no_depth\\test\\gt\\%d.png', x));
    MSE = MSE + immse(gt, result);
end
mean_MSE_no_depth = MSE / 10

MSE = 0;
for x = 0:9
    result = imread(sprintf('result\\sphere_in_cornell_no_normal_depth\\%d.png', x));
    gt = imread(sprintf('dataset\\sphere_in_cornell_no_normal_depth\\test\\gt\\%d.png', x));
    MSE = MSE + immse(gt, result);
end
mean_MSE_no_normal_depth = MSE / 10

