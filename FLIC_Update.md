# FLIC structure in a Nutshell

```abnf
Manifest      := Name? SecurityCtx? (EncryptedNode / Node) 
EncryptedNode := OCTET* AuthTag? ; Encrypted Node + AEAD Tag
SecurityCtx   := AlgorithmId AlgorithmData
AlgorithmId   := PresharedKey / RsaKem / INTEGER
AlgorithmData := PresharedKeyData / RsaKemData / OCTET* ; Algorithm dependent data

Node          := NodeData? HashGroup+

NodeData      := SubtreeSize? SubtreeDigest? Locators?
SubtreeSize   := INTEGER
SubtreeDigest := HashValue
Locators      := Final? Link+
Final         := TRUE / FALSE
HashValue     := ; See RFC 8506
Link          := ; See RFC 8506

HashGroup     := GroupData? Pointers
Pointers      := HashValue+
GroupData     := LeafSize? LeafDigest? SubtreeSize? SubtreeDigest? SizeIndex? Locators?
LeafSize      := INTEGER
LeafDigest    := HashValue
SizeIndex     := INTEGER+ ; Array of integers same size as Ptr array

PresharedKey     := %x0001
PresharedKeyData := KeyNum IV Mode
KeyNum           := INTEGER
IV               := OCTET+
Mode             := AES-GCM-128 AES-GCM-256

RsaKem        := %0x0002
RsaKemData    := KeyId IV Mode WrappedKey LocatorPrefix
KeyId         := HashValue
WrappedKey    := OCTET+
LocatorPrefix := Link
```

## Field Descriptions:

*	Name: The optional ContentObject name
*	SecurityCtx: Information about how to decrypt an EncryptedNode.  The structure will depend on the specific encryption algorithm.
*	AlgorithmId: The ID of the encryption method (e.g. preshared key, a broadcast encryption scheme, etc.)
*	AlgorithmData: The context for the encryption algorithm.
*	EncryptedNode: An opaque octet string with an optional authentication tag (i.e. for AEAD authentication tag)
*	Node: A plain-text manifest node.  The structure allows for in-place encryption/decryption.
*	NodeData: the metadata about the Manifest node
*	SubtreeSize: The size of all application data at and below the Node
*	SubtreeDigest: The cryptographic digest of all application data at and below the Node
*	Locators: An array of routing hints to find the manifest components
*	Final: A flag that prevents Locators from being superseded by a child Manifest Node
*	HashGroup: A set of child pointers and associated metadata
*	GroupData: Metadata that applies to a HashGroup
*	LeafSize: Size of all application data immediately under the Group (i.e. without recursion through other Manifests)
*	LeafDigest: Digest of all application data immediately under the Group
*	SubtreeSize: Size of all application data under the Group (i.e., with recursion)
*	SubtreeDigest: Digest of all application data under the Group (i.e. with recursion)
*	SizeIndex: An array of the same size as the Ptr array with the recursive size of application data under that Ptr
*	Ptr: The ContentObjectHash of a child, which may be a data ContentObject (i.e. with Payload) or another Manifest Node.
*	PresharedKey related fields are described below under Preshared Key Algorithm

## Example of a full Manifest node, such as a root manifest

```bash
[FIXED_HEADER OCTET[8]]
(ContentObject/T_OBJECT
   (Name/T_NAME ...)
   (ExpiryTime/T_EXPIRY 20190630Z000000)
   (Manifest
      (Node
         (NodeData
            (SubtreeSize 5678)
            (SubtreeDigest (HashValue SHA256 a1b2...))
            (Locators (Final FALSE) (Link /example.com/repo))
         )
         (HashGroup
            (GroupData
              (SubtreeSize 1234)
              (SubtreeDigest (HashValue SHA256 abcd...))
            )
            (Ptr ...)
            (Ptr ...)
         )
      ) 
   )
)
(ValidationAlg ...)
(ValidationPayload ...)
```

## Encrypted Manifest Example
To use an encrypted manifest, create an unencrypted manifest with the SecurityCtx and AuthTag, then do an
in-place encryption with AES-GCM-256.  Put the Authentication Tag in the AuthTag value.  After the encryption,
change the TLV type of Node to EncryptedNode.

Note that if the publisher should finish the encryption and TLV type changes before signing the ContentObject with the ValidationPayload.

```bash
[FIXED_HEADER OCTET[8]]
(ContentObject/T_OBJECT
   (Name/T_NAME ...)
   (ExpiryTime/T_EXPIRY 20190630Z000000)
   (Manifest
      (SecurityCtx
          (PresharedKey (KeyNum 55) (IV 8585...) (Mode AES-GCM-256))
      )
      (Node
         (NodeData
            (SubtreeSize 5678)
            (SubtreeDigest (HashValue SHA256 a1b2...))
            (Locators (Final FALSE) (Link /example.com/repo))
         )
         (HashGroup
            (GroupData
              (SubtreeSize 1234)
              (SubtreeDigest (HashValue SHA256 abcd...))
            )
            (Ptr ...)
            (Ptr ...)
         )
      )
      (AuthTag 0x00...) 
   )
)
(ValidationAlg ...)
(ValidationPayload ...)
```


## Example of a nameless and encrypted manifest node

```bash
[FIXED_HEADER OCTET[8]]
(ContentObject/T_OBJECT
   (ExpiryTime/T_EXPIRY 20190630Z000000)
   (Manifest
      (SecurityCtx
          (PresharedKey (KeyNum 55) (IV 8585...) (Mode AES-GCM-256))
      )
      (EncryptedNode ...)
      (AuthTag ...)
   )
)

; After in-place decryption, change type of EncryptedNode to Node
; and change overwrite AuthTag with a zeroed PAD.

[FIXED_HEADER OCTET[8]]
(ContentObject/T_OBJECT
   (ExpiryTime/T_EXPIRY 20190630Z000000)
   (Manifest
      (SecurityCtx
          (PresharedKey (KeyNum 55) (IV 8585...) (Mode AES-GCM-256))
      )
      (Node ...)
      (PAD ...)
   )
)
```


## PresharedKey Algorithm

```abnf
PresharedKeyData := KeyNum IV Mode
KeyNum           := INTEGER
IV               := OCTET+
Mode             := AES-GCM-128 AES-GCM-256
```

The KeyNum identifies a key on the receiver.  The key must be of the correct length of the Mode used.  If the key is longer, use the left bits. Many receivers many have the same key with the same KeyId.

A publisher creates a signed root manifest with a security context.   A consumer must ensure that the root manifest signer is the expected publisher for use with the pre-shared key, which may be shared with many other consumers.  The publisher may use either method 8.2.1 (deterministic IV) or 8.2.2 (RBG-based IV) [NIST 800-38D] for creating the IV. 

Each encrypted manifest node (root manifest or internal manifest) has a full security context (KeyNum, IV, Mode).  The AES-GCM decryption is independent for each manifest so Manifest objects can be fetched and decrypted in any order.  This design also ensures that if a manifest tree points to the same subtree repeatedly,  such as for deduplication, the decryptions are all idempotent.

The functions for authenticated encryption and authenticated decryption are as given in Sections 7.1 and 7.2 of NIST 800-38D: GCM-AE_K(IV, P, A) and GCM-AD_K(IV, C, A, T).

```bash
EncryptNode(SecurityCtx, Node, K, IV) -> GCM-AE_K(IV, P, A) -> (C, T)
Node: The wire format of the Node (P)
SecurityCtx: The wire format of the SecurityCtx as the Additional Authenticated Data (A)
K: the pre-shared key (128 or 256 bits)
IV: The initialization vector (usually 96 or 128 bits)
C: The cipher text
T: The authentication tag
```

The pair (C,T) is the OpaqueNode encoded as a TLV structure:
(OpaqueNode (CipherText C) (AuthTag T))

DecryptNode(SecurityCtx, C, T, K, IV) -> GCM-AD_K (IV, C, A, T) -> (Node, FailFlag)

Node: The wire format of the decrypted Node
FailFlag: Indicates authenticated decryption failure (true or false)

If doing in-place decryption, the cipher text C will be enclosed in an EncryptedNode TLV value.  After decryption, change the TLV type to Node.  The length should be the same.  After decryption the AuthTag is no longer needed.  The TLV type should be changed to T_PAD and the value zeroed.  The SecurityCtx could be changed to T_PAD and zeroed or left as-is.

## RSA Key Encapsulation Method

- See also RFC 5990
- See also NIST SP 800-56B Rev. 2
- See also https://lists.w3.org/Archives/Public/public-xmlsec/2009May/att-0032/Key_Encapsulation.pdf

In this system, a key manager (KM) (which could be the publisher) creates a Content Encryption Key (CEK) and a key wrapping pair with a Key Encryption Key (KEK) and Key Decryption Key (KDK).   Each publisher and consumer has its own public/private key pair, and the KM knows each publisher’s and consumer’s identity and its public key (PK_x). 

We do not describe the publisher-key manager protocol to request a CEK.  The publisher will obtain the (CEK, E_KEK(Z), KeyId, Locator), where each element is: the content encryption key, the CEK precursor, Z, encrypted with the KEK (an RSA operation), and the KeyId of the corresponding KDK, and the Locator is the CCNx name prefix to fetch the KDK (see below).  The precursor Z is chosen randomly z < n-1, where n is KEK’s public modulus.  Note that CEK = KDF(Z).  Note that the publisher does not see KEK or Z.

We use HKDF (RFC 5869) for the KDF.  CEK = HKDF-Expand(HKDF-Extract(0, Z), ‘CEK’, KeyLen), where KenLen is usually 32 bytes (256 bits).

```abnf
RsaKemData    := KeyId IV Mode WrappedKey LocatorPrefix
KeyId         := HashValue
IV            := OCTET+
Mode          := AES-GCM-128 AES-GCM-256
WrappedKey    := OCTET+
LocatorPrefix := Link
```

- KeyId: the ID of the KDK
- IV: The initialization vector for AES-GCM
- Mode: The encryption mode for the Manifest’s EncryptedNode value
- WrappedKey: E_KEK(Z)
- LocatorPrefix: Link with name = KM prefix, KeyId = KM KeyId

To fetch the KDK, a consumer with public key PK_c constructs an Interest with name `/LocatorPrefix/<KeyId>/<PK_c keyid>` and a KeyIdRestriction of the KM’s KeyId (from the LocatorPrefix Link).  It should receive back a signed Content Object with the KDK wrapped for the consumer, or a NAK from the KM.  The payload of the ContentObject will be RsaKemWrap(PK, KDK).  The signed ContentObject must have a KeyLocator to the KM’s public key.  The consumer will trust the KM’s public key because the publisher, whom the consumer trusts, relayed that KeyId inside its own signed Manifest.  The signed Content Object should have an ExpiryTime, which may be shorter than the Manifest’s, but should not be substantially longer than the Manifest’s ExpiryTime.  The KM may decide how to handle the Recommended Cache Time, or if caching of the response is even permissible.  The KM may require on-line fetching of the response via a CCNxKE encrypted transport tunnel.

```bash
RsaKemWrap(PK, K, KeyLen = 256):
  choose a z < n-1, where n is PK’s public modulus
  encrypt c = z^e mod n
  prk = HKDF-Extract(0, Z)
  kek = HKDF-Expand(prk, ‘RsaKemWrap’, KeyLen)
  wrap WK = E_KEK(K) [AES-WRAP, RFC 3394]
  output (c, WK)
```

A consumer must verify the signed content object’s signature against the Key Manager’s public key.  The consumer then unwraps the KDK from the Content Object’s payload using RsaKemUnwrap().  The KeyLen is taken from the WrapMode parameter.

```bash
RsaKemUnwrap(SK, c, WK, KeyLen = 256):
  Using the consumers private key SK, decrypt Z from c.
  prk = HKDF-Extract(0, Z)
  kek = HKDF-Expand(prk, ‘RsaKemWrap’, KeyLen)
  K = D_KEK(WK) [AES-UNWRAP, RFC 33940]
  output K
```

The consumer then unwraps the CEK precursor by using the KDK to decrypt Z.  It then derives CEK as above.

Manifest encryption and decryption proceed as with PresharedKey, but using the CEK.

## Broadcast Encryption Method
*WORK IN PROGRESS*

See Boneh, Dan, Craig Gentry, and Brent Waters. "Collusion resistant broadcast encryption with short ciphertexts and private keys." In Annual International Cryptology Conference, pp. 258-275. Springer, Berlin, Heidelberg, 2005.

The Key Manager (KM) knows all consumers and each consumers RSA/EC public key.  Each consumer has an ID

The publisher requests a key from the KM for a set of consumers identities or pre-defined groups, and receives (HDR, K, KeyId(PK), S, LocatorPrefix).

```abnf
BEMData := KeyId IV Mode HDR S LocatorPrefix
```

