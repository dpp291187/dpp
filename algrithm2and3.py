import math

def infer_sbox_dimension(Sbox):
    """Infer n for an n×n S-box from its length."""
    size = len(Sbox)
    if size == 0 or (size & (size - 1)) != 0:
        raise ValueError("S-box length must be a power of two (2^n).")

    n = size.bit_length() - 1

    max_val = max(Sbox)
    if max_val >= (1 << n):
        raise ValueError(
            f"Maximum S-box value = {max_val}, exceeds {n}-bit range "
            f"(max allowed = {(1 << n) - 1})."
        )

    return n, size


def calculate_boolean_functions(Sbox, n=None):

    #Extract Boolean coordinate functions from S-box.

    if n is None:
        n, size = infer_sbox_dimension(Sbox)
    else:
        size = 1 << n
        if len(Sbox) != size:
            raise ValueError(f"S-box must have {size} entries when n = {n}.")

    boolean_functions_sbox = []

    for bit_idx in range(n):
        bits = []
        for x in range(size):  # input values 0 .. size-1
            bit = (Sbox[x] >> bit_idx) & 1
            bits.append('1' if bit else '0')
        boolean_functions_sbox.append("".join(bits))

    return boolean_functions_sbox


def idx_to_permutation(idx, n):

    max_val = math.factorial(n)
    idx_mod = idx % max_val  # wrap idx into [0, n!-1]

    digits = [0] * n
    rem = idx_mod

    # Compute digits d0..d_{n-1}
    for i in range(n):
        f = math.factorial(n - 1 - i)  # (n-1-i)!
        if f > 0:
            digits[i] = rem // f
            rem %= f
        else:
            digits[i] = 0

    # Build permutation from digits
    L = list(range(n))
    perm = []
    for d in digits:
        perm.append(L.pop(d))

    return perm


def compute_s_box_output_array_fixed_idx_verilog(Sbox, idx=0, neg_index=None):

    # Infer n and size from S-box
    n, size = infer_sbox_dimension(Sbox)

    # Step 1: extract Boolean coordinate functions
    f = calculate_boolean_functions(Sbox, n=n)

    # Optional: negate one coordinate function (bitwise NOT)
    if neg_index is not None:
        if not (0 <= neg_index < n):
            raise ValueError(f"neg_index must be in [0, {n-1}], got {neg_index}")
        inv_bits = ''.join('1' if b == '0' else '0' for b in f[neg_index])
        f[neg_index] = inv_bits

    # Step 2: idx -> permutation on n output bits
    perm = idx_to_permutation(idx, n)

    output_array = []

    # Step 3: apply permutation to each S-box output
    for x in range(size):
        # Pack bits from MSB (bit n-1) to LSB (bit 0)
        combined_bits = ''.join(f[bit_idx][x] for bit_idx in range(n - 1, -1, -1))

        # Apply perm: perm[i] is index in combined_bits
        permuted_bits = ''.join(combined_bits[perm[i]] for i in range(n))

        # Convert to hex
        o_b_hex = hex(int(permuted_bits, 2))
        output_array.append(o_b_hex)

    return output_array


def print_coordinate_functions_for_verilog(Sbox):
    """Print Boolean coordinate functions as bit strings (for Verilog)."""
    n, size = infer_sbox_dimension(Sbox)
    f = calculate_boolean_functions(Sbox, n=n)

    for i, bits in enumerate(f):
        print(f"// f[{i}] - output bit {i}, input 0..{size - 1}")
        print(f"// Length: {len(bits)} bits")
        print(f"f[{i}] = \"{bits}\";")
        print()


PRESENT = [0xc, 0x5, 0x6, 0xb, 0x9, 0x0, 0xa, 0xd, 0x3, 0xe, 0xf, 0x8, 0x4, 0x7, 0x1, 0x2]

AES = [
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x1, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x4, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x5, 0x9a, 0x7, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x9, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x0, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x2, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0xc, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0xb, 0xdb,
    0xe0, 0x32, 0x3a, 0xa, 0x49, 0x6, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x8,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x3, 0xf6, 0xe, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0xd, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0xf, 0xb0, 0x54, 0xbb, 0x16
]


if __name__ == "__main__":
    # Example: PRESENT 4×4 S-box
    Sbox = PRESENT

    # Example 1: only permutation, no negation
    out_perm_only = compute_s_box_output_array_fixed_idx_verilog(
        Sbox, idx=21, neg_index=None
    )

    # Example 2: negate f0 (LSB) and no permutation (idx = 0)
    out_neg_f0 = compute_s_box_output_array_fixed_idx_verilog(
        Sbox, idx=0, neg_index=0
    )

    print("S_dyn with permutation only (idx = 21):")
    print(", ".join(out_perm_only))

    print("\nS_dyn with f0 negated and no permutation (idx = 0):")
    print(", ".join(out_neg_f0))
