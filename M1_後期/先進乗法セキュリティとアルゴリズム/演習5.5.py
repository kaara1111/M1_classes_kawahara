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
    # assert type(K) == bytes or type(K) == str
    # assert len(K) == 32 or len(K) == 64
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

def ec_dsa_sign(m,x,G,l,r,a,p):
    shake = shake256(m,l.bit_length())
    U = aff_ec_exp(a,G[0],G[1],r,p)
    u = U[0]%l
    if u == 0:
        r = random.randint(1,l-1)
        return ec_dsa_sign(m,x,G,l,r,a,p)
    v = (inv(r,l)*(shake+x*u))%l
    if v == 0:
        r = random.randint(1,l-1)
        return ec_dsa_sign(m,x,G,l,r,a,p)
    return u,v
    
def ec_dsa_verify(signature,m,Y,G,l,a,p):
    shake = shake256(m,l.bit_length())
    d = inv(signature[1],l)
    mdG = aff_ec_exp(a,G[0],G[1],(shake*d)%l,p)
    udY = aff_ec_exp(a,Y[0],Y[1],(signature[0]*d)%l,p)
    U = aff_ec_add(mdG[0],mdG[1],udY[0],udY[1],p)
    return U[0]%l == signature[0]

def main():
    n = 115792089210356248762697446949407573529996955224135760342422259061068512044369
    a = -3
    b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
    gx = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296
    gy = 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
    p = 2**256-2**224 + 2**192 + 2**96-1
    k0,k1,k2 = 8,8,16

    # SK = 27077763127661076507477261512997103447780673270796970849255477399292372780398
    # PK = (84546812694622314234645652022815970258631217784135599287049648644983010139605, 62074767048292746179747235898686980422491711536393340602868877577748039401698)

    # x = 125792089210356248262697496949407573629996953224135760348422359061668512044368
    # x = x % 2**256
    x =  107177752448117308908071655440637252326265510361800063218696951564287110941962
    Y_kawahara = (47722760402257809832165565742720090643087167288062589650051101927774446241812, 39021276127894944885857989445618536208698722404721939052798699871475305257270)
    
    Y_ta = (23124520933866442928347675279410463221357657037396410043984275938653804469905, 77379747179401226453628642476400928329889461627058848362905712683190336255129)

    # 以前の暗号文
    # Cm= 86013057502025334134883288444712707164409217410918149092794049958332523674587929208634118887467132171851753888108651970974504517530288565144627422718710217363911311089674686933449502084107891278256660470329799326638386540430335826049687414840537189709616789181945150256470466243512277930361356765152252969228534271068605210449988691517348064745166725837631346541847629039397359760980026366073844087912565169030859866334409378696694061900088131275515638188432641286910653563506980092740385756523401497650984575296555197559086113514084267802154483262039467601499826467320930388361773485405666620696686767251913046779967388273470287447012549172277095377228475132287352373091005423883817655295274552697994292898963706848464884615732338198167609993001910454251641636776473028469593903570297003026347167306210164617849138431833518408369920081868637960156946239149993152521632456472201814342914200865206146588359129739473426690919766615106160209817273032323266446877137221647215409219156565649851505150530615484983942562533863942580576646875706816418838592509918309666761384117665436687830704906447561959725471147083319572284562876398464088279945945307807157678599794699180750771130996905282153235463457523067256585764263508988637080651274736122080568674605591035175155995079181090502330367725771151624155610174060465620630592381022804547743650626964939049423323035772086718729127895702016445071163217481476842329869270851844055322504587834776853520570952937068473261894477261287099977990734052835316397448412915420465138120974387921855611386207510333581387281867830884075665400572189800424851888714860087771263890584626656932698568663540051646726120116297340011078916876417546227562773279895769662709494885011371263472551573819385159611972118734349898262054004894583
    # CK= [(58607444170589253205409864825657487918174849772590899158459921363879585763124, 34968894788277986398737123784723493040737822732065189923377935768196271794332), 107086111156433184203495431711509868887189223429192905884016414977373350842431]
    # signature= [21542452202257016873217703937509720739451869323912491148934232627495788813014, 62649934736221488367461580793889832363189060426955414557243443442125124924637]
    
    Cm= 163129549235592535178776512947680499382376033529303624822313736770430141362226549745701553549314295328253964420085086179204915270155014545664313401462502729205853593869013311046963855045826914408115609440064861247692284992806955127687880874372947746296287492855279185375696567701147085538954411889385899807687157041947771962033950895414576993212557633275069813280651469946759946672197724336054530356243576730161014036862359411813977390106114467611863614810271176161491965375693692511162829677343835534965599187402004682144688735759338046147431775514551486820761354690500753142680804758822068374389839541504527158030735118073758966685722989133462775026457110839604791608685393325910593431210997086589267084887796165506733238265662091180952121175248538452442947592546005448005109776581355007805914288385894561039228883816521404161997905197472522289466895417445907842843419701303605401657714769866727038582718045957132659188652406583716900885554216904297657590356438214493395263749586746560161640889591157510939506453436787693398654767564195464185842197997930071301967524849717811021628445693374446687046553727562517901281511482380870324433976605972536419689176430804229593269033139884337240366337512035711518566315515404786907333285940124637363078756300356490548039316484387133794966890083651185668964000891696800507584823880172845485255642839160042213456134711157755074358929080503272948019049199553447588410879569466627761360704757928909721453115992885357332914035703442176785148182252846237082353651772013795725913145853630407449779201636918520268707878827093857834899422121359051680166605067328546585205004195229269213502394704911821195628000765433026306393649978881262596452077648577976454783450345376450212257207061434084604431021784226047634633549230193872
    CK= [(58607444170589253205409864825657487918174849772590899158459921363879585763124, 34968894788277986398737123784723493040737822732065189923377935768196271794332), 5769681524562955432480898100481193678624904066452121147594862252063713768200]
    signature= [97993539563661187581441134614631294588985960212574335483634752358525862645117, 87104312979547637235104478260959018426189346309879396431050198129020505468399]

    CK_dec = ec_elgamal_oaep_dec(CK,k0,k1,k2,a,x,p)
    # print("CK_dec:",CK_dec)

    Cm = Cm.to_bytes((Cm.bit_length() + 7)//8, byteorder='big')
    Cm_dec = chacha20enc(CK_dec, Cm).decode("utf-8")
    print(Cm_dec)

    if ec_dsa_verify(signature,Cm_dec,Y_ta,(gx,gy),n,a,p):
        print("OK")
    else:
        print("NG")

    ans = "データに署名を施してから収集者に送信するようにすることで，データセットの汚染を防ぐことができると考えられる． 大阪大学 川原尚己"

    r = random.randint(1,n-1)
    sig = ec_dsa_sign(ans,x,(gx,gy),n,r,a,p)
    print("回答の署名：",sig)

    Key = hex(random.randint(2**255, 2**256-1))[2:]
    ans_enc = chacha20enc(Key, ans.encode("utf-8"))
    ans_enc = int.from_bytes(ans_enc, byteorder='big')
    print("共通鍵：",Key)
    print("回答の暗号文：",ans_enc)
    
    r1 = random.randint(1,n-1)
    r2 = hex(random.randint(2**(8*k0-1),2**(8*(k0))-1))[2:]
    Key_enc = ec_elgamal_oaep_enc(Key, k0,k1,k2, a,gx,gy,Y_ta[0],Y_ta[1],p,r1,r2)
    print("共通鍵の暗号文：",Key_enc)


if __name__ == '__main__':
    main()