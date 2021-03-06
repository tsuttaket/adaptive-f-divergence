from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf
from models import GaussianMixture

class Model():

    def __init__(self, config, p_target,
                    scope_name = 'f_divergence', is_train=True):

        self.config = config
        self.p_target  = p_target

        with tf.variable_scope(scope_name) as scope:
            if self.config.proposal == 'mixture':
                n_components = 20
                self._mu = tf.get_variable('mu', shape=(n_components, self.config.dim), dtype=tf.float32,
                                        initializer=tf.random_uniform_initializer(-15., 15.))

                self._log_var = tf.get_variable('log_var', 
                        initializer = np.ones((n_components, self.config.dim)).astype('float32'),
                        dtype=tf.float32)

                self._weights = tf.get_variable('weights',
                        initializer = tf.ones(n_components) / n_components, 
                        dtype=tf.float32)

                self.q_approx = GaussianMixture(n_components, self._mu, self._log_var, self._weights, is_train=True)
            else:
                raise NotImplementedError

        self.q_train_vars = [self._mu, self._log_var, self._weights]

        self.loss = self.get_f_div_loss(self.config.sample_size)
        tf.summary.scalar("loss", self.loss)


    def get_f_div_loss(self, n_samples):
        samples = self.q_approx.sample(n_samples)

        logp = self.p_target.log_prob(samples, stop_grad=True)
        logq = self.q_approx.log_prob(samples)

        wx = self.phi(n_samples, logp, logq, self.config.method, alpha=self.config.alpha)
        loss = tf.reduce_sum(tf.stop_gradient(tf.expand_dims(wx, axis=1)*(self.q_approx.log_gradient(samples) - self.p_target.log_gradient(samples))) * samples)
        return loss


    def phi(self, n_samples, logp, logq, method='adapted', alpha = -1):
        diff = logp - logq

        if method == 'adapted':
            # \#(t_i < t)
            diff -= tf.reduce_max(diff)
            dx = tf.exp(diff)
            prob = tf.sign(tf.expand_dims(dx, 1) - tf.expand_dims(dx, 0))  
            prob = tf.cast(tf.greater(prob, 0.5), tf.float32)
            wx = tf.reduce_sum(prob, axis=1) / n_samples
            wx = (1. - wx) ** alpha ## beta = -1; or beta = -0.5
        elif method == 'alpha':
            diff = alpha * diff
            diff -= tf.reduce_max(diff)
            wx = tf.exp(diff)
        else:
            raise NotImplementedError

        wx /= tf.reduce_sum(wx)  # normalization
        return wx


    def sample(self, n_samples):
        return self.q_approx.sample(n_samples)



