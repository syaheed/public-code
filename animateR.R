rm(list = ls())
graphics.off()

path = '/home/syaheed/Desktop/animateR/'
setwd(path)

x = 1:360

for (phase in x){
    y = sin(pi*(x+phase) / 180)
    tiff(paste0('plot_',sprintf('%05d',phase),'.tiff'), width = 6, height = 4, units = 'in', res = 100)
    plot(x,y, ylim =  c(-1,1), main = sprintf('Phase Shift = %d degree', phase))
    dev.off()
}

system('ffmpeg -i "plot_%05d.tiff" -r 24 -y animated.mp4')
