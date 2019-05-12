import os
from options.test_options import TestOptions
from data import CreateDataLoader
from models import create_model
from util.visualizer import save_images
from util import html


def fnorm(x):
    return sqrt((x**2).sum())

def score(y_true, y_pred):
    return 100*(1 - 2*fnorm(y_true - y_pred) / (fnorm(y_true) + fnorm(y_pred))) 


if __name__ == '__main__':
    opt = TestOptions().parse()
    # hard-code some parameters for test
    opt.num_threads = 1   # test code only supports num_threads = 1
    opt.batch_size = 1    # test code only supports batch_size = 1
    opt.serial_batches = True  # no shuffle
    opt.no_flip = True    # no flip
    opt.display_id = -1   # no visdom display
    data_loader = CreateDataLoader(opt)
    dataset = data_loader.load_data()
    model = create_model(opt)
    model.setup(opt)
    # create a website
    web_dir = os.path.join(opt.results_dir, opt.name, '%s_%s' % (opt.phase, opt.epoch))
    webpage = html.HTML(web_dir, 'Experiment = %s, Phase = %s, Epoch = %s' % (opt.name, opt.phase, opt.epoch))
    # test with eval mode. This only affects layers like batchnorm and dropout.
    # pix2pix: we use batchnorm and dropout in the original pix2pix. You can experiment it with and without eval() mode.
    # CycleGAN: It should not affect CycleGAN as CycleGAN uses instancenorm without dropout.
    if opt.eval:
        model.eval()

    total_acc, count = 0, 0
    for i, data in enumerate(dataset):
        #if i >= opt.num_test:
        #    break
        model.set_input(data)
        model.test()
        visuals = model.get_current_visuals()
        img_path = model.get_image_paths()
        #if i % 5 == 0:
        print('processing (%04d)-th image... %s' % (i, img_path), end="")
        save_images(webpage, visuals, img_path, aspect_ratio=opt.aspect_ratio, width=opt.display_winsize)
    
        acc = score(model.real_A, model.fake_B)
        print("Acc:", acc)
        total_acc += acc
        count += 1

    print("Accuracy: %.2f." % total_acc / count)
    # save the website
    webpage.save()
