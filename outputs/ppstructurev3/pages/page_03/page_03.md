<div style="text-align: center;">Table 1: Maximum path lengths, per-layer complexity and minimum number of sequential operations for different layer types. n is the sequence length, d is the representation dimension, k is the kernel size of convolutions and r the size of the neighborhood in restricted self-attention.</div>



<div style="text-align: center;"><html><body><table border="1"><tr><td>Layer Type</td><td>Complexity per Layer</td><td>Sequential Operations</td><td>Maximum Path Length</td></tr><tr><td>Self-Attention</td><td>$\overline{{O(n^{2}\cdot d)}}$</td><td>O(1)</td><td>O(1)</td></tr><tr><td>Recurrent</td><td>$O(n\cdot d^{2})$</td><td>O(n)</td><td>$O(n)$</td></tr><tr><td>Convolutional</td><td>$O(\vec{k}\cdot n\cdot\vec{d}^{2})$</td><td>O(1)</td><td>$O(l o g_{k}(n))$</td></tr><tr><td>Self-Attention (restricted)</td><td>$O(r\cdot n\cdot d)$</td><td>O(1)</td><td>$O(n/r)$</td></tr></table></body></html></div>


### 3.5 Positional Encoding 

Since our model contains no recurrence and no convolution, in order for the model to make use of the order of the sequence, we must inject some information about the relative or absolute position of the tokens in the sequence. To this end, we add "positional encodings" to the input embeddings at the bottoms of the encoder and decoder stacks. The positional encodings have the same dimension $d_{\mathrm{m o d e l}}$ |as the embeddings, so that the two can be summed. There are many choices of positional encodings,learned and fi xed [9].



In this work, we use sine and cosine functions of different frequencies:

$$\begin{aligned}PE_{(pos,2i)}=sin(pos/10000^{2i/d_{model}})\\PE_{(pos,2i+1)}=cos(pos/10000^{2i/d_{model}})\end{aligned}$$

where pos is the position and i is the dimension. That is, each dimension of the positional encoding corresponds to a sinusoid. The wavelengths form a geometric progression from 2π to $10000\cdot2\tau$ T. We chose this function because we hypothesized it would allow the model to easily learn to attend by relative positions, since for any fixed offset k,$P E_{p o s+k}$ can be represented as a linear function of 

$P E_{p o s}$ 

1



We also experimented with using learned positional embeddings [9] instead, and found that the two versions produced nearly identical results (see Table 3 row (E)). We chose the sinusoidal version because it may allow the model to extrapolate to sequence lengths longer than the ones encountered during training.



## 4 Why Self-Attention 

In this section we compare various aspects of self-attention layers to the recurrent and convolutional layers commonly used for mapping one variable-length sequence of symbol representations $(x_{1},...,x_{n})$ to another sequence of equal length $(z_{1},...,z_{n})$ ,with $x_{i},z_{i}\in\mathbb{R}^{d}$ ,such as a hidden layer in a typical sequence transduction encoder or decoder. Motivating our use of self-attention we consider three desiderata.



One is the total computational complexity per layer. Another is the amount of computation that can be parallelized, as measured by the minimum number of sequential operations required.

The third is the path length between long-range dependencies in the network. Learning long-range dependencies is a key challenge in many sequence transduction tasks. One key factor affecting the ability to learn such dependencies is the length of the paths forward and backward signals have to traverse in the network. The shorter these paths between any combination of positions in the input and output sequences, the easier it is to learn long-range dependencies [12]. Hence we also compare the maximum path length between any two input and output positions in networks composed of the different layer types.



As noted in Table 1, a self-attention layer connects all positions with a constant number of sequentially executed operations, whereas a recurrent layer requires $O(n)$  sequential operations. In terms of computational complexity, self-attention layers are faster than recurrent layers when the sequence 