import {Config} from '@remotion/cli/config';

// PNG (não JPEG) nos quadros intermediários: com JPEG a pele saía ~5 níveis mais vermelha no MP4 (medido no Paper:
// still PNG e render com PNG = cor da gravação; render com JPEG = +5 R, +3 G, -3 B). REGRA: a cor da pessoa nunca muda.
// Junto com --color-space=bt709 no render (os scripts render_paper.sh e render_a3d.sh já põem).
Config.setVideoImageFormat('png');
Config.setOverwriteOutput(true);
Config.setCodec('h264');
Config.setCrf(18);
Config.setConcurrency(4);
