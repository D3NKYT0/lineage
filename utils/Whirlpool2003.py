import struct

class Whirlpool2003:
    BLOCK_SIZE = 64
    DIGEST0 = (
        "19FA61D75522A4669B44E39C1D2E1726C530232130D407F89AFEE0964997F7A7"
        "3E83BE698B288FEBCF88E3E03C4F0757EA8964E59B63D93708B138CC42A66EB3"
    )
    R = 10

    Sd = (
        "\u1823\uc6E8\u87B8\u014F\u36A6\ud2F5\u796F\u9152"
        "\u60Bc\u9B8E\uA30c\u7B35\u1dE0\ud7c2\u2E4B\uFE57"
        "\u1577\u37E5\u9FF0\u4AdA\u58c9\u290A\uB1A0\u6B85"
        "\uBd5d\u10F4\ucB3E\u0567\uE427\u418B\uA77d\u95d8"
        "\uFBEE\u7c66\udd17\u479E\ucA2d\uBF07\uAd5A\u8333"
        "\u6302\uAA71\uc819\u49d9\uF2E3\u5B88\u9A26\u32B0"
        "\uE90F\ud580\uBEcd\u3448\uFF7A\u905F\u2068\u1AAE"
        "\uB454\u9322\u64F1\u7312\u4008\uc3Ec\udBA1\u8d3d"
        "\u9700\ucF2B\u7682\ud61B\uB5AF\u6A50\u45F3\u30EF"
        "\u3F55\uA2EA\u65BA\u2Fc0\udE1c\uFd4d\u9275\u068A"
        "\uB2E6\u0E1F\u62d4\uA896\uF9c5\u2559\u8472\u394c"
        "\u5E78\u388c\ud1A5\uE261\uB321\u9c1E\u43c7\uFc04"
        "\u5199\u6d0d\uFAdF\u7E24\u3BAB\ucE11\u8F4E\uB7EB"
        "\u3c81\u94F7\uB913\u2cd3\uE76E\uc403\u5644\u7FA9"
        "\u2ABB\uc153\udc0B\u9d6c\u3174\uF646\uAc89\u14E1"
        "\u163A\u6909\u70B6\ud0Ed\ucc42\u98A4\u285c\uF886"
    )

    T0 = [0] * 256
    T1 = [0] * 256
    T2 = [0] * 256
    T3 = [0] * 256
    T4 = [0] * 256
    T5 = [0] * 256
    T6 = [0] * 256
    T7 = [0] * 256
    rc = [0] * R

    valid = None

    @classmethod
    def _init_tables(cls):
        if hasattr(cls, "_tables_initialized"):
            return
        ROOT = 0x11d
        S = [0] * 256
        for i in range(256):
            c = ord(cls.Sd[i >> 1])
            s = ((c >> 8) if (i & 1) == 0 else c) & 0xFF
            s2 = s << 1
            if s2 > 0xFF:
                s2 ^= ROOT
            s3 = s2 ^ s
            s4 = s2 << 1
            if s4 > 0xFF:
                s4 ^= ROOT
            s5 = s4 ^ s
            s8 = s4 << 1
            if s8 > 0xFF:
                s8 ^= ROOT
            s9 = s8 ^ s
            S[i] = s
            t = (
                (s << 56) | (s << 48) | (s4 << 40) | (s << 32) |
                (s8 << 24) | (s5 << 16) | (s2 << 8) | s9
            )
            cls.T0[i] = t & 0xFFFFFFFFFFFFFFFF
            cls.T1[i] = ((t >> 8) | (t << 56)) & 0xFFFFFFFFFFFFFFFF
            cls.T2[i] = ((t >> 16) | (t << 48)) & 0xFFFFFFFFFFFFFFFF
            cls.T3[i] = ((t >> 24) | (t << 40)) & 0xFFFFFFFFFFFFFFFF
            cls.T4[i] = ((t >> 32) | (t << 32)) & 0xFFFFFFFFFFFFFFFF
            cls.T5[i] = ((t >> 40) | (t << 24)) & 0xFFFFFFFFFFFFFFFF
            cls.T6[i] = ((t >> 48) | (t << 16)) & 0xFFFFFFFFFFFFFFFF
            cls.T7[i] = ((t >> 56) | (t << 8)) & 0xFFFFFFFFFFFFFFFF
        r = 1
        i = 0
        j = 0
        while r < cls.R + 1:
            cls.rc[i] = (
                (S[j] << 56) | (S[j+1] << 48) | (S[j+2] << 40) | (S[j+3] << 32) |
                (S[j+4] << 24) | (S[j+5] << 16) | (S[j+6] << 8) | S[j+7]
            )
            i += 1
            j += 8
            r += 1
        cls._tables_initialized = True

    def __init__(self):
        self._init_tables()
        self.H = [0] * 8
        self.count = 0
        self.buffer = bytearray()
        self._reset_context()

    def _reset_context(self):
        for i in range(8):
            self.H[i] = 0

    def update(self, data):
        if isinstance(data, str):
            data = data.encode("utf-8")
        self.buffer += data
        self.count += len(data)
        while len(self.buffer) >= self.BLOCK_SIZE:
            self._transform(self.buffer[:self.BLOCK_SIZE])
            self.buffer = self.buffer[self.BLOCK_SIZE:]

    def _transform(self, block):
        # Converte o bloco em 8 inteiros de 64 bits
        n = [int.from_bytes(block[i*8:(i+1)*8], "big") for i in range(8)]
        k = self.H[:]
        nn = [n[i] ^ k[i] for i in range(8)]
        w = [0] * 8
        for r in range(self.R):
            # Key schedule
            Kr = [
                self.T0[(k[0] >> 56) & 0xFF] ^ self.T1[(k[7] >> 48) & 0xFF] ^
                self.T2[(k[6] >> 40) & 0xFF] ^ self.T3[(k[5] >> 32) & 0xFF] ^
                self.T4[(k[4] >> 24) & 0xFF] ^ self.T5[(k[3] >> 16) & 0xFF] ^
                self.T6[(k[2] >> 8) & 0xFF] ^ self.T7[k[1] & 0xFF] ^ self.rc[r]
            ]
            for i in range(1, 8):
                Kr.append(
                    self.T0[(k[i] >> 56) & 0xFF] ^ self.T1[(k[(i-1)%8] >> 48) & 0xFF] ^
                    self.T2[(k[(i-2)%8] >> 40) & 0xFF] ^ self.T3[(k[(i-3)%8] >> 32) & 0xFF] ^
                    self.T4[(k[(i-4)%8] >> 24) & 0xFF] ^ self.T5[(k[(i-5)%8] >> 16) & 0xFF] ^
                    self.T6[(k[(i-6)%8] >> 8) & 0xFF] ^ self.T7[k[(i-7)%8] & 0xFF]
                )
            k = Kr
            # Cipher output
            w = [
                self.T0[(nn[0] >> 56) & 0xFF] ^ self.T1[(nn[7] >> 48) & 0xFF] ^
                self.T2[(nn[6] >> 40) & 0xFF] ^ self.T3[(nn[5] >> 32) & 0xFF] ^
                self.T4[(nn[4] >> 24) & 0xFF] ^ self.T5[(nn[3] >> 16) & 0xFF] ^
                self.T6[(nn[2] >> 8) & 0xFF] ^ self.T7[nn[1] & 0xFF] ^ Kr[0]
            ]
            for i in range(1, 8):
                w.append(
                    self.T0[(nn[i] >> 56) & 0xFF] ^ self.T1[(nn[(i-1)%8] >> 48) & 0xFF] ^
                    self.T2[(nn[(i-2)%8] >> 40) & 0xFF] ^ self.T3[(nn[(i-3)%8] >> 32) & 0xFF] ^
                    self.T4[(nn[(i-4)%8] >> 24) & 0xFF] ^ self.T5[(nn[(i-5)%8] >> 16) & 0xFF] ^
                    self.T6[(nn[(i-6)%8] >> 8) & 0xFF] ^ self.T7[nn[(i-7)%8] & 0xFF] ^ Kr[i]
                )
            nn = w[:]
        # Miyaguchi-Preneel
        for i in range(8):
            self.H[i] ^= w[i] ^ n[i]

    def _pad_buffer(self):
        n = (self.count + 33) % self.BLOCK_SIZE
        padding = 33 if n == 0 else self.BLOCK_SIZE - n + 33
        result = bytearray([0x80] + [0] * (padding - 9))
        bits = self.count * 8
        result += bits.to_bytes(8, "big")
        return result

    def digest(self):
        # Salva o estado atual
        H_save = self.H[:]
        count_save = self.count
        buffer_save = self.buffer[:]
        # Padding
        self.update(self._pad_buffer())
        # Resultado
        result = b''.join(h.to_bytes(8, "big") for h in self.H)
        # Restaura o estado
        self.H = H_save
        self.count = count_save
        self.buffer = buffer_save
        return result

    def hexdigest(self):
        return self.digest().hex().upper()

    def self_test(self):
        if self.valid is None:
            self.valid = self.hexdigest() == self.DIGEST0
        return self.valid

# Exemplo de uso:
# whirlpool = Whirlpool2003()
# whirlpool.update(b"mensagem")
# print(whirlpool.hexdigest())

if __name__ == '__main__':
    import base64
    whirlpool = Whirlpool2003()
    whirlpool.update(b"yang")
    # Opção 1: Usar o digest() diretamente (recomendado)
    hash_b64 = base64.b64encode(whirlpool.digest()).decode()
