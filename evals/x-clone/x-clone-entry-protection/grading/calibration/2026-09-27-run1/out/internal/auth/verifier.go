package auth

import (
	"context"
	"errors"
	"sync"
	"time"
)

// Verifier は、トークンの署名と発行者と有効期間を確かめる。
type Verifier struct {
	issuer  string
	jwksURL string
	mu      sync.Mutex
	keys    map[string][]byte
}

// NewVerifier は、発行者と鍵の一覧の URL から Verifier を作る。
func NewVerifier(issuer, jwksURL string) *Verifier {
	return &Verifier{issuer: issuer, jwksURL: jwksURL, keys: map[string][]byte{}}
}

type claims struct {
	kid string
	iss string
	sub string
	exp time.Time
}

// Verify は、トークンを確かめて主体を返す。手元に無い鍵の識別子が来たら、鍵の一覧を取り直す。
func (v *Verifier) Verify(ctx context.Context, token string) (Subject, error) {
	c, err := parse(token)
	if err != nil {
		return "", err
	}
	v.mu.Lock()
	key, ok := v.keys[c.kid]
	v.mu.Unlock()
	if !ok {
		if err := v.refresh(ctx); err != nil {
			return "", err
		}
		v.mu.Lock()
		key, ok = v.keys[c.kid]
		v.mu.Unlock()
		if !ok {
			return "", errors.New("未知の鍵")
		}
	}
	if err := verifySignature(token, key); err != nil {
		return "", err
	}
	if c.iss != v.issuer {
		return "", errors.New("発行者が違う")
	}
	if time.Now().After(c.exp) {
		return "", errors.New("期限切れ")
	}
	return Subject(c.sub), nil
}

func (v *Verifier) refresh(ctx context.Context) error {
	keys, err := fetchJWKS(ctx, v.jwksURL)
	if err != nil {
		return err
	}
	v.mu.Lock()
	v.keys = keys
	v.mu.Unlock()
	return nil
}

func parse(string) (claims, error)         { return claims{}, errors.New("省略") }
func verifySignature(string, []byte) error { return errors.New("省略") }
func fetchJWKS(context.Context, string) (map[string][]byte, error) {
	return nil, errors.New("省略")
}
