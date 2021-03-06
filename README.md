# Variational Inference with Tail-adaptive f-Divergence

This repository contains a tensorflow implementation for tail-adaptive f-divergence, as presented in the followng paper:

[Dilin Wang](http://cs.utexas.edu/~dilin), [Hao Liu](http://haoliu.site/), [Qiang Liu](https://www.cs.utexas.edu/~lqiang/), ["Variational Inference with Tail-adaptive f-Divergence"](https://nips.cc/Conferences/2018/Schedule?showEvent=11559), NIPS 2018.


## Our Algorithm

Our tail-adaptive weights ($\gamma_f$ in Eqn 8) could be easily calculated with the following function,

```python
def get_tail_adaptive_weights(self, l_p, l_q, beta=-1.):
    """returns the tail-adaptive weights
    Args:
        l_p: log p(x), 1-d tensor, log probability of p
        l_q: log q(x), 1-d tensor, log probability of q
        beta: magnitude, default -1
    Returns:
        Tail-adaptive weights
    """
    diff = l_p - l_q
    diff -= tf.reduce_max(diff)
    dx = tf.exp(diff)
    prob = tf.sign(tf.expand_dims(dx, 1) - tf.expand_dims(dx, 0))
    prob = tf.cast(tf.greater(prob, 0.5), tf.float32)
    wx = tf.reduce_sum(prob, axis=1) / tf.cast(tf.size(l_p), tf.float32)
    wx = (1. - wx) ** beta # beta = -1; or beta = -0.5
    
    wx /= tf.reduce_sum(wx)  # self-normalization
    return tf.stop_gradient(wx)
```


## Citation
If you find tail-adaptive f-divergence useful in your research, please consider citing:

        @article{wang2018variational,
          title={Variational Inference with Tail-adaptive f-Divergence},
          author={Wang, Dilin and Liu, Hao and Liu, Qiang},
          journal={arXiv preprint arXiv:1810.11943},
          year={2018}
        }

