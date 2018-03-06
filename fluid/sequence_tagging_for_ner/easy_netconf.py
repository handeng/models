import paddle.v2.fluid as fluid
from paddle.v2.fluid.initializer import NormalInitializer
from utils import logger, load_dict, get_embedding
import math

def ner_net(word_dict_len, label_dict_len, stack_num=2, is_train=True):
    mark_dict_len = 2
    word_dim = 50
    mark_dim = 5
    hidden_dim = 300
    IS_SPARSE = True
    embedding_name = 'emb'
    stack_num = 2

    word = fluid.layers.data(
        name='word', shape=[1], dtype='int64', lod_level=1)

    word_embedding = fluid.layers.embedding(
        input=word,
        size=[word_dict_len, word_dim],
        dtype='float32',
        is_sparse=IS_SPARSE,
        param_attr=fluid.ParamAttr(
                name=embedding_name, trainable=True))
   
    mark = fluid.layers.data(
        name='mark', shape=[1], dtype='int64', lod_level=1)

    mark_embedding = fluid.layers.embedding(
        input=mark,
        size=[mark_dict_len, mark_dim],
        dtype='float32',
        is_sparse=IS_SPARSE)

    #print dir(word_embedding)
    #print word_embedding.shape
    #print word_embedding.to_string
   # print mark_embedding.to_string("")

    gru_h, c = fluid.layers.dynamic_lstm(input=word_embedding, size=hid_dim, is_reverse=False)
    gru_max = fluid.layers.sequence_pool(input=gru_h, pool_type='max', act='tanh')
    fc1 = fluid.layers.fc(input=gru_max, size=hid_dim2, act='tanh')
    prediction = fluid.layers.fc(input=fc1, size=label_dict_len, act='softmax')
'''
    cost = fluid.layers.cross_entropy(input=prediction, label=label)
    avg_cost = fluid.layers.mean(x=cost)
    sgd_optimizer = fluid.optimizer.SGD(learning_rate=0.001)

    word_caps_vector = fluid.layers.concat(input=[word_embedding, mark_embedding], axis = 1)
    mix_hidden_lr = 1e-3
    
    rnn_para_attr = fluid.ParamAttr(
        initializer=NormalInitializer(loc=0.0, scale=0.0, seed=0), learning_rate=0.1) 
    hidden_para_attr = fluid.ParamAttr(
        initializer=NormalInitializer(loc=0.0, scale=(1. / math.sqrt(hidden_dim) / 3), seed=0),
        learning_rate=mix_hidden_lr)

    hidden = fluid.layers.fc(
        input=word_caps_vector,
        name="__hidden00__",
        size=hidden_dim,
        act="tanh",
        bias_attr=fluid.ParamAttr(
            initializer=NormalInitializer(loc=0.0, scale=(1. / math.sqrt(hidden_dim) / 3), seed=0)),
        param_attr=fluid.ParamAttr(
            initializer=NormalInitializer(loc=0.0, scale=(1. / math.sqrt(hidden_dim) / 3), seed=0)))
    fea = []
    for direction in ["fwd", "bwd"]:
        for i in range(stack_num):
            if i != 0:
                #print i
                #print rnn.shape
                #print hidden.shape
                #print isinstance(hidden, fluid.framework.Variable)
                #print isinstance(rnn, fluid.framework.Variable)
                #print dir(rnn)
		#print type(rnn)
                #print rnn[0].shape
		#print rnn[1].shape
		#print rnn[2].shape
                hidden = fluid.layers.fc(
                    name="__hidden%02d_%s__" % (i, direction),
                    size=hidden_dim,
                    act="stanh",
                    bias_attr=fluid.ParamAttr(initializer=NormalInitializer(loc=0.0, scale=1.0, seed=0)),
                    input=[hidden, rnn[0], rnn[1]],
                    param_attr=[hidden_para_attr, rnn_para_attr, rnn_para_attr])
            rnn = fluid.layers.dynamic_lstm(
                name="__rnn%02d_%s__" % (i, direction),
                input=hidden,
		size=hidden_dim,
                candidate_activation='relu',
                gate_activation='sigmoid',
                cell_activation='sigmoid',
                bias_attr=fluid.ParamAttr(initializer=NormalInitializer(loc=0.0, scale=1.0, seed=0)),
                is_reverse=(i % 2) if direction == "fwd" else not i % 2,
                param_attr=rnn_para_attr)
        fea += [hidden, rnn[0], rnn[1]]

    rnn_fea = fluid.layers.fc(
        size=hidden_dim,
        bias_attr=fluid.ParamAttr(initializer=NormalInitializer(loc=0.0, scale=(1. / math.sqrt(hidden_dim) / 3), seed=0)),
        act="stanh",
        input=fea,
        param_attr=[hidden_para_attr, rnn_para_attr, rnn_para_attr] * 2)

    emission = fluid.layers.fc(size=label_dict_len,
        input=rnn_fea,
        param_attr=fluid.ParamAttr(initializer=NormalInitializer(loc=0.0, scale=(1. / math.sqrt(hidden_dim) / 3), seed=0)))
    '''
    if is_train:
        target = fluid.layers.data(
            name="target",
            shape=[1], dtype='int64', lod_level=1)
        
        crf_cost = fluid.layers.linear_chain_crf(
            input=prediction,
            label=target,
            param_attr=fluid.ParamAttr(
                name='crfw',
                initializer=NormalInitializer(loc=0.0, scale=(1. / math.sqrt(hidden_dim) / 3), seed=0),
                learning_rate=mix_hidden_lr))

        crf_decode = fluid.layers.crf_decoding(
            input=emission,
            label=target,
            param_attr=fluid.ParamAttr(name='crfw'))

        return crf_cost, crf_decode, word, mark, target
    else:
        predict = fluid.layers.crf_decoding(
            input=emission,
            param_attr=fluid.ParamAttr(name='crfw'))
        return predict    
