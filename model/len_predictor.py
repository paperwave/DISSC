import torch
from torch import nn


class LenPredictor(nn.Module):
    def __init__(self, token_dict_size=100, spk_dict_size=199, emb_size=32):
        super(LenPredictor, self).__init__()

        self.token_emb = nn.Embedding(token_dict_size + 1, emb_size, padding_idx=token_dict_size)
        self.spk_emb = nn.Embedding(spk_dict_size + 1, emb_size, padding_idx=spk_dict_size)
        self.leaky = nn.LeakyReLU()
        self.dropout = nn.Dropout(p=0.5)

        self.cnn1 = nn.Conv1d(2 * emb_size, 128, kernel_size=(3,), padding=1)
        self.bn1 = nn.BatchNorm1d(128)
        self.cnn11 = nn.Conv1d(128, 128, kernel_size=(3,), padding=1)
        self.bn11 = nn.BatchNorm1d(128)
        self.cnn12 = nn.Conv1d(128, 128, kernel_size=(3,), padding=1)
        self.bn12 = nn.BatchNorm1d(128)

        self.cnn2 = nn.Conv1d(128, 1, kernel_size=(3,), padding=1)

    def forward(self, seq, spk_id):
        emb_seq = self.token_emb(seq)
        emb_spk = torch.repeat_interleave(self.spk_emb(spk_id), seq.shape[-1], dim=1)
        emb_seq = torch.cat([emb_seq, emb_spk], dim=-1)

        cnn1 = self.leaky(self.dropout(self.bn1(self.cnn1(emb_seq.transpose(1, 2)))))
        cnn1 = self.leaky(self.dropout(self.bn11(self.cnn11(cnn1))))
        cnn1 = self.leaky(self.dropout(self.bn12(self.cnn12(cnn1))))
        return self.cnn2(cnn1).squeeze(1)