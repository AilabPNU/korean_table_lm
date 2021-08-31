import modeling
import tensorflow as tf

import numpy as np
import math



def Fully_Connected(inp, output, name, activation, initializer_range=3e-7, reuse=False):
    h = tf.contrib.layers.fully_connected(
        inputs=inp,
        num_outputs=output,
        activation_fn=activation,
        weights_initializer=tf.contrib.layers.xavier_initializer(),
        weights_regularizer=tf.contrib.layers.l2_regularizer(scale=3e-7),
        biases_initializer=tf.constant_initializer(3e-7),
        scope=name,
        reuse=reuse
    )

    return h


def attention_layer_(from_tensor,
                    to_tensor,
                    attention_mask=None,
                    size_per_head=512):
  # Take the dot product between "query" and "key" to get the raw
  # attention scores.
  # `attention_scores` = [B, N, F, T], [B, F, H], [B, T, H] => [B, F, T]
  attention_scores = tf.matmul(from_tensor, to_tensor, transpose_b=True)
  attention_scores = tf.multiply(attention_scores,
                                 1.0 / math.sqrt(float(size_per_head)))

  if attention_mask is not None:
    # `attention_mask` = [B, 1, F, T]
    adder = (1.0 - tf.cast(attention_mask, tf.float32)) * -10000.0
    attention_scores += adder

  # Normalize the attention scores to probabilities.
  # `attention_probs` = [B, N, F, T]
  attention_probs = tf.nn.softmax(attention_scores)

  # `context_layer` = [B, F, T] [B, T, H]
  context_layer = tf.matmul(attention_probs, to_tensor)

  return context_layer


def gelu(x):
    """Gaussian Error Linear Unit.

    This is a smoother version of the RELU.
    Original paper: https://arxiv.org/abs/1606.08415
    Args:
      x: float Tensor to perform activation.

    Returns:
      `x` with the GELU activation applied.
    """
    cdf = 0.5 * (1.0 + tf.tanh(
        (np.sqrt(2 / np.pi) * (x + 0.044715 * tf.pow(x, 3)))))
    return x * cdf


def seq_length(sequence):
    used = tf.sign(tf.reduce_max(tf.abs(sequence), reduction_indices=2))
    length = tf.reduce_sum(used, reduction_indices=1)
    length = tf.cast(length, tf.int32)
    return length


def create_initializer(initializer_range=0.02):
    """Creates a `truncated_normal_initializer` with the given range."""
    return tf.truncated_normal_initializer(stddev=initializer_range)


def masked_softmax(logits, mask, dim):
    exp_mask = (1 - tf.cast(mask, 'float')) * (-1e30)  # -large where there's padding, 0 elsewhere
    masked_logits = tf.add(logits, exp_mask)  # where there's padding, set logits to -large
    prob_dist = tf.nn.softmax(masked_logits, dim)
    return masked_logits, prob_dist


def get_variables_with_name(name, train_only=True, printable=False):
    """Get variable list by a given name scope.
    Examples
    ---------
    >>> dense_vars = tl.layers.get_variable_with_name('dense', True, True)
    """
    print("  [*] geting variables with %s" % name)
    # tvar = tf.trainable_variables() if train_only else tf.all_variables()
    if train_only:
        t_vars = tf.trainable_variables()
    else:
        try: # TF1.0
            t_vars = tf.global_variables()
        except: # TF0.12
            t_vars = tf.all_variables()

    d_vars = [var for var in t_vars if name in var.name]
    if printable:
        for idx, v in enumerate(d_vars):
            print("  got {:3}: {:15}   {}".format(idx, v.name, str(v.get_shape())))
    return d_vars


class KoNET:
    def __init__(self, firstTraining, testCase=False):
        self.first_training = firstTraining

        self.save_path = '/home/ai/pycharm_project/table_qa_adv/model.ckpt'
        self.bert_path = '/home/ai/pycharm2/roberta_table/bert_model.ckpt'

        self.input_ids = tf.placeholder(shape=[None, None], dtype=tf.int32)
        self.input_segments = tf.placeholder(shape=[None, None], dtype=tf.int32)
        self.input_positions = tf.placeholder(shape=[None, None], dtype=tf.int32)
        self.input_mask = tf.placeholder(shape=[None, None], dtype=tf.int32)
        self.input_cols = tf.placeholder(shape=[None, None], dtype=tf.int32)
        self.input_rows = tf.placeholder(shape=[None, None], dtype=tf.int32)

        self.keep_prob = 0.9
        if testCase is True:
            self.keep_prob = 1.0

        self.testCase = testCase

        self.sess = None
        self.prediction_start = None
        self.prediction_stop = None

        self.column_size = 50
        self.row_size = 250

    def create_model(self, input_ids, input_mask, input_segments, is_training=True, reuse=False, scope_name='bert'):
        bert_config = modeling.BertConfig.from_json_file('roberta_base.json')

        if self.testCase is True:
            is_training = False

        model = modeling.BertModel(
            config=bert_config,
            is_training=is_training,
            input_ids=input_ids,
            input_mask=input_mask,
            token_type_ids=input_segments,
            scope='roberta',
            reuse=reuse
        )

        bert_variables = tf.global_variables()

        sequence_output = model.get_sequence_output()

        column_memory, row_memory = self.Table_Memory_Network(sequence_output=sequence_output, hops=3)
        # bert_variables = tf.global_variables()

        row_one_hot = tf.one_hot(self.input_rows, depth=100)
        column_one_hot = tf.one_hot(self.input_cols, depth=50)

        column_memory = tf.matmul(column_one_hot, column_memory)
        row_memory = tf.matmul(row_one_hot, row_memory)

        sequence_output = tf.concat([column_memory, row_memory, sequence_output], axis=2)

        with tf.variable_scope("table_memory_hidden"):
            sequence_output = Fully_Connected(sequence_output, output=768, name='column_wise', activation=None)

        return model, bert_variables, sequence_output

    def get_qa_probs(self, model_output, is_training=False):
        """Get Start/Stop probs for MRC"""

        keep_prob = 0.9

        if is_training is False:
            keep_prob = 1.0

        with tf.variable_scope("MRC_block"):
            model_output = Fully_Connected(model_output, output=768, name='hidden1', activation=tf.nn.leaky_relu)
            model_output = tf.nn.dropout(model_output, keep_prob=keep_prob)

            model_output = Fully_Connected(model_output, output=512, name='hidden2', activation=tf.nn.leaky_relu)
            model_output = tf.nn.dropout(model_output, keep_prob=keep_prob)

        with tf.variable_scope("pointer_net1"):
            log_probs_s = Fully_Connected(model_output, output=1, name='pointer_start1', activation=None, reuse=False)
            log_probs_e = Fully_Connected(model_output, output=1, name='pointer_stop1', activation=None, reuse=False)
            log_probs_s = tf.squeeze(log_probs_s, axis=2)
            log_probs_e = tf.squeeze(log_probs_e, axis=2)

        return log_probs_s, log_probs_e

    def Table_Memory_Network(self, sequence_output, hops=1, dropout=0.2):
        # sequence_output = sequence_output + space_states
        row_one_hot = tf.one_hot(self.input_rows, depth=100)
        row_one_hot = tf.transpose(row_one_hot, perm=[0, 2, 1])

        column_one_hot = tf.one_hot(self.input_cols, depth=50)
        column_one_hot = tf.transpose(column_one_hot, perm=[0, 2, 1])

        column_wise_memory = tf.matmul(column_one_hot, sequence_output)
        row_wise_memory = tf.matmul(row_one_hot, sequence_output)

        reuse = False

        with tf.variable_scope("table_output_layer"):
            with tf.variable_scope("tab_mem"):
                cell_fw_col = tf.nn.rnn_cell.GRUCell(768)
                cell_fw_col = tf.nn.rnn_cell.DropoutWrapper(cell_fw_col, input_keep_prob=self.keep_prob,
                                                            output_keep_prob=self.keep_prob)
                cell_fw_row = tf.nn.rnn_cell.GRUCell(768)
                cell_fw_row = tf.nn.rnn_cell.DropoutWrapper(cell_fw_row, input_keep_prob=self.keep_prob,
                                                            output_keep_prob=self.keep_prob)

                for h in range(hops):
                    print('hop:', h)
                    with tf.variable_scope("column_memory_block", reuse=reuse):
                        column_wise_memory = attention_layer_(
                            from_tensor=column_wise_memory,
                            to_tensor=sequence_output,
                            attention_mask=column_one_hot,
                        )

                    column_wise_memory = Fully_Connected(column_wise_memory, 768, 'hidden_col' + str(0), gelu,
                                                         reuse=reuse)
                    column_wise_memory = modeling.dropout(column_wise_memory, dropout)

                    with tf.variable_scope("row_memory_block", reuse=reuse):
                        row_wise_memory = attention_layer_(
                            from_tensor=row_wise_memory,
                            to_tensor=sequence_output,
                            attention_mask=row_one_hot)

                    row_wise_memory = Fully_Connected(row_wise_memory, 768, 'hidden_row' + str(0), gelu, reuse=reuse)
                    row_wise_memory = modeling.dropout(row_wise_memory, dropout)

                    reuse = True

                # todo: RNN Code for Context Encoding
                with tf.variable_scope("rnn_model_col"):
                    column_wise_memory, state_fw = tf.nn.dynamic_rnn(
                        inputs=column_wise_memory, cell=cell_fw_col,
                        sequence_length=seq_length(column_wise_memory), dtype=tf.float32, time_major=False)

                with tf.variable_scope("rnn_model_row"):
                    row_wise_memory, state_fw = tf.nn.dynamic_rnn(
                        inputs=row_wise_memory, cell=cell_fw_row,
                        sequence_length=seq_length(row_wise_memory), dtype=tf.float32, time_major=False)

        return column_wise_memory, row_wise_memory
