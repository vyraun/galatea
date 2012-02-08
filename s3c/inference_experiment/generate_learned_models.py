from pylearn2.utils import serial

count = 0

for dataset in [ 'stl', 'cifar' ]:
    for kind in [ 'full', 'patch' ]:

        dataset_str = { 'stlfull' : '${STL10_WHITENED_UNSUP}',
                    'stlpatch' : '${STL10_PATCHES_6x6}',
                    'cifarfull' : '${CIFAR10_WHITENED_TRAIN}',
                    'cifarpatch' : '${CIFAR10_PATCHES_6x6}'
                    }[dataset+kind]

        for size in [ 'small', 'med', 'big' ]:

            N = { 'small' : 625, 'med' : 1600, 'big' : 4000 }[size]

            directory = 'models/%s/%s/%s' % (dataset, kind, size)
            path = '%s/learned.yaml' % (directory)

            serial.mkdir(directory)

            f = open(path,'w')

            count += 1

            if count % 2 == 0:
                e_step = """!obj:galatea.s3c.s3c.E_Step {
                        "h_new_coeff_schedule" : [ .1, .1, .1, .1, .1, .1, .1, .1, .2, .2, .2, .3, .3, .3, .4, .4, .4, .4, .4 ],
                        "s_new_coeff_schedule" : [  .7, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1, .1 ],
                        "clip_reflections" : 1,
                        #"monitor_em_functional" : 1
               },"""
            else:
                e_step = """
                !obj:galatea.s3c.s3c.E_Step_CG_Shared {
                        "h_new_coeff_schedule" : [ .1, .1, .1, .1, .1, .1, .1, .1, .2, .2, .2, .3, .3, .3, .4, .4, .4, .4, .4 ],
                        "s_max_iters" : [  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
               },
                """

            f.write("""
!obj:pylearn2.scripts.train.Train {
    "dataset": !pkl: &src "%s",
    "model": !obj:galatea.s3c.s3c.S3C {
               "nvis" : 108,
               "nhid" : %d,
               "init_bias_hid" : -4.,
               "max_bias_hid" : 0.,
               "min_bias_hid" : -7.,
               "irange"  : .02,
               "constrain_W_norm" : 1,
               "init_B"  : 3.,
               "min_B"   : .1,
               "max_B"   : 1e6,
               "tied_B" :  1,
               "init_alpha" : 1.,
               "min_alpha" : 1e-3,
               "max_alpha" : 1e6,
               "init_mu" : 0.,
               "random_patches_src" : *src,
               "print_interval" : 10000,
               "monitor_functional" : 1,
               "monitor_params" : [ 'B', 'p', 'alpha', 'mu', 'W' ],
               "e_step" : %s
               #"learn_after" : 1000,
               "m_step"     : !obj:galatea.s3c.s3c.Grad_M_Step {
                        "learning_rate" : 0.001,
                        "B_learning_rate_scale" : 0.01,
                        "W_learning_rate_scale" : 10.,
                        "p_penalty" : 1.,
                        "B_penalty" : 1.,
                        "alpha_penalty" : 1.
               }
        },
    "algorithm": !obj:pylearn2.training_algorithms.default.DefaultTrainingAlgorithm {
               "batch_size" : 100,
               "batches_per_iter" : 100,
        },
    "save_path": "${PYLEARN2_TRAIN_FILE_NAME}.pkl"
}""" % (dataset_str,N,e_step))

            f.close()

            print 'train.py '+path
