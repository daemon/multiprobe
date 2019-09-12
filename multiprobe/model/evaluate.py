import torch


def hook_bert_layer_output(bert_model, layer_idx, hook):
    bert_model.encoder.layer[layer_idx].register_forward_hook(hook)


def hook_bert_layer_attn(bert_model, layer_idx, hook):
    bert_model.encoder.layer[layer_idx].attention.self.register_forward_hook(hook)


def hook_bert_word_embeddings(bert_model, hook):
    bert_model.embeddings.word_embeddings.register_forward_hook(hook)


class SingleInputBundle(object):

    def __init__(self, sentences, id_map, max_len=256):
        sentences = [x[:max_len - 2] for x in sentences]
        self.sentences = [['[CLS]'] + x + ['[SEP]'] for x in sentences]
        padded_sentences = [x + ['[PAD]'] * (max_len - len(x)) for x in self.sentences]
        self.token_ids = torch.tensor([list(map(id_map.__getitem__, x)) for x in padded_sentences])
        self.input_mask = torch.tensor([([1] * len(x)) + ([0] * (max_len - len(x))) for x in self.sentences])
        self.segment_ids = torch.tensor([[0] * max_len for _ in sentences])

    def cuda(self):
        self.token_ids = self.token_ids.cuda()
        self.input_mask = self.input_mask.cuda()
        self.segment_ids = self.segment_ids.cuda()
        return self

    def mean(self, tensor):
        mask = self.input_mask.unsqueeze(-1).expand_as(tensor).float()
        return (tensor * mask).sum(1) / mask.sum(1)
