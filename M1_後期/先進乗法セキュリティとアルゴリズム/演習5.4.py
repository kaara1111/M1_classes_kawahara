import struct
import binascii
import random
import hashlib
import math

try:
    import psyco            # a specializing [runtime] compiler
    have_psyco = True       # for 32-bit architectures
    print('psyco enabled')
except:
    have_psyco = False

#-----------------------------------------------------------------------

class ChaCha(object):
    """
        ChaCha is an improved variant of Salsa20.
        
        Salsa20 was submitted to eSTREAM, an EU stream cipher
        competition.  Salsa20 was originally defined to be 20
        rounds.  Reduced round versions, Salsa20/8 (8 rounds) and
        Salsa20/12 (12 rounds), were later submitted.  Salsa20/12
        was chosen as one of the winners and 12 rounds was deemed
        the "right blend" of security and efficiency.  Salsa20 
        is about 3x-4x faster than AES-128.
        
        Both ChaCha and Salsa20 accept a 128-bit or a 256-bit key 
        and a 64-bit IV to set up an initial 64-byte state.  For 
        each 64-bytes of data, the state gets scrambled and XORed 
        with the previous state.  This new state is then XORed 
        with the input data to produce the output.  Both being 
        stream ciphers, their encryption and decryption functions 
        are identical.  
        
        While Salsa20's diffusion properties are very good, some 
        claimed the IV/keystream correlation was too strong for 
        comfort.  To satisfy, another variant called XSalsa20 
        implements a 128-bit IV.  For the record, EU eSTREAM team 
        did select Salsa20/12 as a solid cipher providing 128-bit 
        security.  
        
        ChaCha is a minor tweak of Salsa20 that significantly 
        improves its diffusion per round.  ChaCha is more secure 
        than Salsa20 and 8 rounds of ChaCha, aka ChaCha8, provides 
        128-bit security.  (FWIW, I have not seen any calls for a 
        128-bit IV version of ChaCha or XChaCha.)  
        
        Another benefit is that ChaCha8 is about 5-8% faster than 
        Salsa20/8 on most 32- and 64-bit PPC and Intel processors.  
        SIMD machines should see even more improvement.  
        
        Sample usage:
          from chacha import ChaCha
          
          cc8 = ChaCha(key, iv)
          ciphertext = cc8.encrypt(plaintext)
          
          cc8 = ChaCha(key, iv)
          plaintext = cc8.decrypt(ciphertext)
        
        Remember, the purpose of this program is educational; it 
        is NOT a secure implementation nor is a pure Python version 
        going to be fast.  Encrypting large data will be less than 
        satisfying.  Also, no effort is made to protect the key or 
        wipe critical memory after use.  
        
        Note that psyco, a specializing compiler somewhat akin to 
        a JIT, can provide a 2x+ performance improvement over 
        vanilla Python 32-bit architectures.  A 64-bit version of 
        psyco does not exist.  See http://psyco.sourceforge.net
        
        For more information about Daniel Bernstein's ChaCha 
        algorithm, please see http://cr.yp.to/chacha.html
        
        All we need now is a keystream AND authentication in the 
        same pass.  
        
        Larry Bugbee
        May 2009     (Salsa20)
        August 2009  (ChaCha)
        rev June 2010
    """

    TAU    = ( 0x61707865, 0x3120646e, 0x79622d36, 0x6b206574 )
    SIGMA  = ( 0x61707865, 0x3320646e, 0x79622d32, 0x6b206574 )
    ROUNDS = 8                         # ...10, 12, 20?

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def __init__(self, key, iv, rounds=ROUNDS):
        """ Both key and iv are byte strings.  The key must be 
            exactly 16 or 32 bytes, 128 or 256 bits respectively.  
            The iv must be exactly 8 bytes (64 bits) and MUST 
            never be reused with the same key.
            
            The default number of rounds is 8.

            If you have several encryptions/decryptions that use 
            the same key, you may reuse the same instance and 
            simply call iv_setup() to set the new iv.  The previous 
            key and the new iv will establish a new state.
        """
        self._key_setup(key)
        self.iv_setup(iv)
        self.rounds = rounds

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def _key_setup(self, key):
        """ key is converted to a list of 4-byte unsigned integers
            (32 bits).

            Calling this routine with a key value effectively resets
            the context/instance.  Be sure to set the iv as well.
        """
        if len(key) not in [16, 32]:
            raise Exception('key must be either 16 or 32 bytes')
        key_state = [0]*16
        if len(key) == 16:
            k = list(struct.unpack('<4I', key))
            key_state[0]  = self.TAU[0]
            key_state[1]  = self.TAU[1]
            key_state[2]  = self.TAU[2]
            key_state[3]  = self.TAU[3]
            key_state[4]  = k[0]
            key_state[5]  = k[1]
            key_state[6]  = k[2]
            key_state[7]  = k[3]
            key_state[8]  = k[0]
            key_state[9]  = k[1]
            key_state[10] = k[2]
            key_state[11] = k[3]
            # 12 and 13 are reserved for the counter
            # 14 and 15 are reserved for the IV

        elif len(key) == 32:
            k = list(struct.unpack('<8I', key))
            key_state[0]  = self.SIGMA[0]
            key_state[1]  = self.SIGMA[1]
            key_state[2]  = self.SIGMA[2]
            key_state[3]  = self.SIGMA[3]
            key_state[4]  = k[0]
            key_state[5]  = k[1]
            key_state[6]  = k[2]
            key_state[7]  = k[3]
            key_state[8]  = k[4]
            key_state[9]  = k[5]
            key_state[10] = k[6]
            key_state[11] = k[7]
            # 12 and 13 are reserved for the counter
            # 14 and 15 are reserved for the IV
        self.key_state = key_state

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def iv_setup(self, iv):
        """ self.state and other working structures are lists of
            4-byte unsigned integers (32 bits).

            The iv is not a secret but it should never be reused 
            with the same key value.  Use date, time or some other
            counter to be sure the iv is different each time, and
            be sure to communicate the IV to the receiving party.
            Prepending 8 bytes of iv to the ciphertext is the usual
            way to do this.

            Just as setting a new key value effectively resets the
            context, setting the iv also resets the context with
            the last key value entered.
        """
        if len(iv) != 8:
            raise Exception('iv must be 8 bytes')
        v = list(struct.unpack('<2I', iv))
        iv_state = self.key_state[:]
        iv_state[12] = 0
        iv_state[13] = 0
        iv_state[14] = v[0]
        iv_state[15] = v[1]
        self.state = iv_state
        self.lastblock_sz = 64      # init flag - unsafe to continue
                                    # processing if not 64

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def encrypt(self, datain):
        """ Encrypt a chunk of data.  datain and the returned value 
            are byte strings.

            If large data is submitted to this routine in chunks,
            the chunk size MUST be an exact multiple of 64 bytes.
            Only the final chunk may be less than an even multiple.
            (This function does not "save" any uneven, left-over 
            data for concatenation to the front of the next chunk.)
            
            The amount of available memory imposes a poorly defined
            limit on the amount of data this routine can process.
            Typically 10's and 100's of KB are available but then,
            perhaps not.  This routine is intended for educational 
            purposes so application developers should take heed.
        """
        if self.lastblock_sz != 64:
            raise Exception('last chunk size not a multiple of 64 bytes')
        dataout = []
        while datain:
            # generate 64 bytes of cipher stream
            stream = self._chacha_scramble();
            # XOR the stream onto the next 64 bytes of data
            dataout.append(self._xor(stream, datain))
            if len(datain) <= 64:
                self.lastblock_sz = len(datain)
                return b''.join(dataout)
            # increment the iv.  In this case we increment words
            # 12 and 13 in little endian order.  This will work 
            # nicely for data up to 2^70 bytes (1,099,511,627,776GB) 
            # in length.  After that it is the user's responsibility 
            # to generate a new nonce/iv.
            self.state[12] = (self.state[12] + 1) & 0xffffffff
            if self.state[12] == 0:           # if overflow in state[12]
                self.state[13] += 1           # carry to state[13]
                # not to exceed 2^70 x 2^64 = 2^134 data size ??? <<<<
            # get ready for the next iteration
            datain = datain[64:]
        # should never get here
        raise Exception('Huh?')
    
    decrypt = encrypt
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    def _chacha_scramble(self):     # 64 bytes in
        """ self.state and other working strucures are lists of
            4-byte unsigned integers (32 bits).

            output must be converted to bytestring before return.
        """
        x = self.state[:]           # makes a copy
        for i in range(0, self.rounds, 2):
            # two rounds per iteration
            self._quarterround(x, 0, 4, 8,12)
            self._quarterround(x, 1, 5, 9,13)
            self._quarterround(x, 2, 6,10,14)
            self._quarterround(x, 3, 7,11,15)
            
            self._quarterround(x, 0, 5,10,15)
            self._quarterround(x, 1, 6,11,12)
            self._quarterround(x, 2, 7, 8,13)
            self._quarterround(x, 3, 4, 9,14)
            
        for i in range(16):
            x[i] = (x[i] + self.state[i]) & 0xffffffff
        output = struct.pack('<16I',
                            x[ 0], x[ 1], x[ 2], x[ 3],
                            x[ 4], x[ 5], x[ 6], x[ 7],
                            x[ 8], x[ 9], x[10], x[11],
                            x[12], x[13], x[14], x[15])
        return output               # 64 bytes out
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    '''
    # as per definition - deprecated
    def _quarterround(self, x, a, b, c, d):
        x[a] = (x[a] + x[b]) & 0xFFFFFFFF
        x[d] = self._rotate((x[d]^x[a]), 16)
        x[c] = (x[c] + x[d]) & 0xFFFFFFFF
        x[b] = self._rotate((x[b]^x[c]), 12)
        
        x[a] = (x[a] + x[b]) & 0xFFFFFFFF
        x[d] = self._rotate((x[d]^x[a]), 8)
        x[c] = (x[c] + x[d]) & 0xFFFFFFFF
        x[b] = self._rotate((x[b]^x[c]), 7)
        
    def _rotate(self, v, n):        # aka ROTL32
        return ((v << n) & 0xFFFFFFFF) | (v >> (32 - n))
    '''
    
    # surprisingly, the following tweaks/accelerations provide 
    # about a 20-40% gain
    def _quarterround(self, x, a, b, c, d):
        xa = x[a]
        xb = x[b]
        xc = x[c]
        xd = x[d]
        
        xa  = (xa + xb)  & 0xFFFFFFFF
        tmp =  xd ^ xa
        xd  = ((tmp << 16) & 0xFFFFFFFF) | (tmp >> 16)  # 16=32-16
        xc  = (xc + xd)  & 0xFFFFFFFF
        tmp =  xb ^ xc
        xb  = ((tmp << 12) & 0xFFFFFFFF) | (tmp >> 20)  # 20=32-12
        
        xa  = (xa + xb)  & 0xFFFFFFFF
        tmp =  xd ^ xa
        xd  = ((tmp <<  8) & 0xFFFFFFFF) | (tmp >> 24)  # 24=32-8
        xc  = (xc + xd)  & 0xFFFFFFFF
        tmp =  xb ^ xc
        xb  = ((tmp <<  7) & 0xFFFFFFFF) | (tmp >> 25)  # 25=32-7
        
        x[a] = xa
        x[b] = xb
        x[c] = xc
        x[d] = xd
    
    def _xor(self, stream, datain):
        lmin = min(len(stream), len(datain))
        return bytes(a ^ b for a, b in zip(stream[:lmin], datain[:lmin]))
    
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    if have_psyco:
        # if you psyco encrypt() and _chacha_scramble() you
        # should get a 2.4x speedup over vanilla Python 2.5.  
        # The other functions seem to offer only negligible 
        # improvement.  YMMV.
        
        _key_setup = psyco.proxy(_key_setup)    # small impact
        iv_setup   = psyco.proxy(iv_setup)      # small impact
        encrypt    = psyco.proxy(encrypt)                   # 18-32%
        _chacha_scramble = psyco.proxy(_chacha_scramble)    # big help, 2x
        _quarterround    = psyco.proxy(_quarterround)       # ???
#        _rotate = psyco.proxy(_rotate)          # minor impact
        _xor    = psyco.proxy(_xor)             # very small impact
        pass

# ChaCha20 暗号化 chacha20enc(K, m)
# Input: 鍵 (16 進文字列, 128bit or 256bit): K, メッセージ(バイト列 (ASCII)): m
# Output: 暗号文 (バイト列): C
# ※この関数はこちらから提供します
def chacha20enc(K, m):
    assert type(K) == bytes or type(K) == str
    assert len(K) == 32 or len(K) == 64
    # assert type(m) == bytes
    
    iv = int.to_bytes(0, 8, byteorder='big')
    key = binascii.unhexlify(K)
    cc = ChaCha(key, iv, rounds=20)
    return cc.encrypt(m)

def Mod(a, b):
    return a%b

def mod_binary(g, k, n, p):
    y=1
    k = str(bin(k))[2:]
    for i in k:
        if i=='1':
            y = Mod(Mod(y**2, p)*g, p)
            # print(y)
        else:
            y = Mod(y**2, p)
            # print(y)
    return y

def inv(a, n):
    # return a^-1 mod n
    return mod_binary(a, n-2, len(str(bin(n-2))[2:]) , n)

def aff_ec_add(x1, y1, x2, y2, p):
    if x1 == math.inf:
        return (x2, y2)
    elif x2 == math.inf:
        return (x1, y1)
    elif x1%p == x2%p and y1%p == -y2%p:
        return (math.inf, math.inf)
    # lam = Fraction((y2-y1)%p, (x2-x1)%p)%p
    lam = ((y2-y1)*inv(x2-x1,p))%p
    x3 = (lam**2 - x1 - x2)%p
    y3 = (lam*(x1-x3) - y1)%p
    return (x3%p, y3%p)

def aff_ec_dbl(x1, y1, a, p):
    if y1 == math.inf or y1%p == 0:
        return (math.inf, math.inf)
    # t = Fraction((3*x1**2+a)%p, 2*y1%p)%p
    t = ((3*(x1**2)+a)*inv(2*y1,p))%p
    x2 = (t**2 - 2*x1)%p
    y2 = (t*(x1-x2) - y1)%p
    return (x2%p, y2%p)

def aff_ec_exp(a, x0, y0, k, p):
    if k == 0:
        return (math.inf,math.inf)
    if k < 0:
        return aff_ec_exp(a, x0, -y0, -k, p)
    (x, y) = (math.inf, math.inf)
    bk = bin(k)[2:]
    for i in bk:
        (x, y) = aff_ec_dbl(x, y, a, p)
        if i == '1':
            (x, y) = aff_ec_add(x, y, x0, y0, p)
    return (x, y)

def ec_elgamal_key_gen(a,x0,y0,p,x):
    gx,gy = aff_ec_exp(a,x0,y0,x,p)
    return gx,gy

def ec_elgamal_enc(m,a,x0,y0,pubx,puby,p,r):
    U = aff_ec_exp(a,x0,y0,r,p)
    V = aff_ec_exp(a,pubx,puby,r,p)
    c = m^V[0]
    return U,c

def ec_elgamal_dec(C,a,x,p):
    V = aff_ec_exp(a,C[0][0],C[0][1],x,p)
    m = V[0]^C[1]
    return m

# shake256(m, ℓ)
# Input: 文字列： m, 出力のビット長 :ℓ
# Output: 整数： mのハッシュ値
def shake256(m, l):
    hash_size = (l//8 +10)
    m1 = hashlib.shake_256(m.encode()).digest(hash_size)
    m2 = int.from_bytes(m1, byteorder='big')
    Hm = m2 >> (m2.bit_length()-l+1)
    return Hm

# MGF(Message Generation Function) mgf(D, oLen)
# Input: データ(16 進文字列) : D, 出力バイト長 : oLen
# Output: D の MGF 出力値 (16進文字列)
def mgf(D, oLen):
    if len(D) % 2 == 1:
        D = '0' + D
    m = binascii.unhexlify(D)
    return hashlib.shake_128(m).hexdigest(oLen)

def xor(a, b):
    return hex(int(a, 16) ^ int(b, 16))[2:]

# def OAEP_enc(m,a,G,SK,PK,p,k0,k1,k2):
# メッセージ (16 進バイト列):m < ℓ (ℓ はベースポイントの位数), OAEP 乱数バイト長 k0, パディングバイト長
# k1, メッセージバイト長: k2, 曲線パラメータ: a, ベースポイント: G = (x0, y0), 公開鍵: Y = (pubx, puby), 法: p, 楕円
# ElGamal 暗号用乱数: r1 < ℓ, OAEP 用乱数 (k0 バイト 16 進バイト列): r2
def ec_elgamal_oaep_enc(m,k0,k1,k2,a,x0,y0,pubx,puby,p,r1,r2):
    Gr = mgf(r2, k1+k2)
    s = xor(Gr, m + '0'*(2*k1))
    Hs = mgf(s, k0)
    t = xor(Hs, r2)
    w = int(s + t,16)

    U,c = ec_elgamal_enc(w,a,x0,y0,pubx,puby,p,r1)
    return U,c

def ec_elgamal_oaep_dec(C,k0,k1,k2,a,x,p):
    k = k0 + k1 + k2
    w = ec_elgamal_dec(C,a,x,p)
    s = hex(w)[2:][:2*(k1+k2)]
    t = hex(w)[2:][2*(k1+k2):2*k]
    r = xor(mgf(s,k0), t)
    z = xor(mgf(r,k1+k2), s)
    m = z[:2*k2]
    chk = z[2*k2:]
    if chk == '0'*(2*k1):
        return m
    else:
        return "Decryption Error"

def main():
    n = 115792089210356248762697446949407573529996955224135760342422259061068512044369
    a = -3
    b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
    gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
    gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
    p = 2**256-2**224 + 2**192 + 2**96-1
    k0,k1,k2 = 8,8,16

    SK = 27077763127661076507477261512997103447780673270796970849255477399292372780398
    PK = (84546812694622314234645652022815970258631217784135599287049648644983010139605, 62074767048292746179747235898686980422491711536393340602868877577748039401698)

    K = hex(random.randint(2**127,2**128-1))[2:]
    r1 = 94942963219160478645616456847425949118405414797801813963145265022204180576071
    r64 = "c8986be43bcfa690"

    C = ec_elgamal_oaep_enc(K,k0,k1,k2,a,gx,gy,PK[0],PK[1],p,r1,r64)

    m = "Two kinds of contemporary developments in cryptography are examined. Widening applications of teleprocessing have given rise to a need for new types of cryptographic systems, which minimize the need for secure key distribution channels and supply the equivalent of a written signature. This paper suggests ways to solve these currently open problems. It also discusses how the theories of communication and computation are beginning to provide the tools to solve cryptographic problems of long standing."
    m = m.encode()
    print("m = ",m)
    C1 = chacha20enc(K,m)
    print("C1 = ",C1)

    C_dec = ec_elgamal_oaep_dec(C,k0,k1,k2,a,SK,p)
    print("type(C_dec) = ",type(C_dec))
    print("type(C1) = ",type(C1))
    C1_dec = chacha20enc(C_dec,C1)
    m_dec = C1_dec.decode()
    print(m_dec)

if __name__ == '__main__':
    main()