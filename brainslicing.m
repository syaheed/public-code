%% clear everthing from memory
clear all; clc; close all;

%% user params

braindir = '/run/media/syaheed/Storage/Dropbox/Waterloo/brain/Anatomical'; % where the dicoms are
saggital = 115; % max = 240, increase = more lateral (rightwards?)
coronal = 180; % max = 240, increase = more posterior
transverse = 60; % max = 150, increase = more dorsal

%% Make 3d Matrix

cd(braindir)
lof = dir('*.dcm');
lof = {lof.name}.';
info = dicominfo(lof{1});
nRows = info.Rows;
nCols = info.Columns;
nFrames = size(lof,1);
Mat = repmat(int16(0), [nRows, nCols, nFrames]);

for p = 1:nFrames
    fname = lof{p};
    X = dicomread(fname);
    Mat(:,:,p) = X;
end

%% sagittal slicing
Ys = squeeze(Mat(:,saggital,:));
Ys = rot90(Ys);

%% coronal 
Yc = squeeze(Mat(coronal,:,:));
Yc = rot90(Yc);

%% transverse 
Yt = squeeze(Mat(:,:,transverse));

%% Join
temp = [Ys Yc];
extra = repmat(int16(0),size(Yt,1),size(temp,2));
final = [temp; extra];
final( size(temp,1)+1 : size(final,1), 1:size(Yt,2)  ) = Yt;

figure();
imshow(final, [0 255])

hold on;
plot([coronal,coronal],[150 0], '-r')
plot([0,240],[150-transverse 150-transverse], '-c')

plot([0,size(Yt,1)],[size(Ys,1)+coronal size(Ys,1)+coronal], '-r')
plot([saggital,saggital],[size(Ys,1)+1 size(final,1)], '-g')

plot([size(Ys,2)+1, size(final,2)],[150-transverse 150-transverse], '-c')
plot([saggital + size(Ys,2), saggital + size(Ys,2)],[0 size(Yc,1)], '-g')

s_text = sprintf('Sagittal: %d', saggital);
t_text = sprintf('Transverse: %d', transverse);
c_text = sprintf('Coronal: %d', coronal);

text(size(Ys,2) + 50, size(Yc,1) + 85, s_text, 'color','g','Fontsize',16)
text(size(Ys,2) + 50, size(Yc,1) + 115, c_text, 'color','r','Fontsize',16)
text(size(Ys,2) + 50, size(Yc,1) + 145, t_text, 'color','c','Fontsize',16)

%figure()
%imshow(Ys, [0 255])
