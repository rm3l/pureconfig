package pure

type Token int

const (
	Illegal Token = iota
	EOF
	WHITESPACE
	GROUP
	INT
	DOUBLE
	STRING
	BOOL
	QUANTITY
	PATH
	ENV
	ARRAY
	INCLUDE
	IDENTIFIER
	EQUALS // =
	COLON  // :
	LPAREN
	RPAREN
	REF // =>
	DOT // .
)
