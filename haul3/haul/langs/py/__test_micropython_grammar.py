#!/bin/python3
"""
Translation of MicroPython's "py/grammar.h" to Python
It is based on the "expand_macros" processed file.

2024-04-07 Bernhard "HotKey" Slawik
"""

# Define some types for interoperability
size_t = int
uint8_t = int
uint16_t = int
uint32_t = int

from __test_micropython_lexer import *

### parse.c constants/enums
RULE_ACT_ARG_MASK = 0x0f
RULE_ACT_KIND_MASK = 0x30
RULE_ACT_ALLOW_IDENT = 0x40
RULE_ACT_ADD_BLANK = 0x80
RULE_ACT_OR = 0x10
RULE_ACT_AND = 0x20
RULE_ACT_LIST = 0x30
RULE_ARG_KIND_MASK = 0xf000
RULE_ARG_ARG_MASK = 0x0fff
RULE_ARG_TOK = 0x1000
RULE_ARG_RULE = 0x2000
RULE_ARG_OPT_RULE = 0x3000


# enum
RULE_file_input	= 0
RULE_file_input_2	= 1
RULE_decorated	= 2
RULE_funcdef	= 3
RULE_simple_stmt_2	= 4
RULE_expr_stmt	= 5
RULE_testlist_star_expr	= 6
RULE_del_stmt	= 7
RULE_pass_stmt	= 8
RULE_break_stmt	= 9
RULE_continue_stmt	= 10
RULE_return_stmt	= 11
RULE_yield_stmt	= 12
RULE_raise_stmt	= 13
RULE_import_name	= 14
RULE_import_from	= 15
RULE_global_stmt	= 16
RULE_nonlocal_stmt	= 17
RULE_assert_stmt	= 18
#if MICROPY_PY_ASYNC_AWAIT
RULE_async_stmt	= 19
#endif
RULE_if_stmt	= 20
RULE_while_stmt	= 21
RULE_for_stmt	= 22
RULE_try_stmt	= 23
RULE_with_stmt	= 24
RULE_suite_block_stmts	= 25
#if MICROPY_PY_ASSIGN_EXPR
RULE_namedexpr_test	= 26
#endif
RULE_test_if_expr	= 27
RULE_lambdef	= 28
RULE_lambdef_nocond	= 29
RULE_or_test	= 30
RULE_and_test	= 31
RULE_not_test_2	= 32
RULE_comparison	= 33
RULE_star_expr	= 34
RULE_expr	= 35
RULE_xor_expr	= 36
RULE_and_expr	= 37
RULE_shift_expr	= 38
RULE_arith_expr	= 39
RULE_term	= 40
RULE_factor_2	= 41
RULE_power	= 42
#if MICROPY_PY_ASYNC_AWAIT
RULE_atom_expr_await	= 43
#else
#endif
RULE_atom_expr_normal	= 44
RULE_atom_paren	= 45
RULE_atom_bracket	= 46
RULE_atom_brace	= 47
RULE_trailer_paren	= 48
RULE_trailer_bracket	= 49
RULE_trailer_period	= 50
#if MICROPY_PY_BUILTINS_SLICE
RULE_subscriptlist	= 51
RULE_subscript_2	= 52
RULE_subscript_3	= 53
#else
#RULE_subscriptlist	= 54
#endif
RULE_testlist	= 54
#if MICROPY_PY_BUILTINS_SET
RULE_dictorsetmaker_item	= 55
#else
#RULE_dictorsetmaker_item	= 57
#endif
RULE_classdef	= 56
#if MICROPY_PY_ASSIGN_EXPR
#else
#endif
RULE_yield_expr	= 57
RULE_const_object	= 58	# special node for a constant, generic Python object
RULE_generic_colon_test	= 59
RULE_generic_equal_test	= 60
RULE_single_input	= 61
RULE_file_input_3	= 62
RULE_eval_input	= 63
RULE_eval_input_2	= 64
RULE_decorator	= 65
RULE_decorators	= 66
#if MICROPY_PY_ASYNC_AWAIT
RULE_decorated_body	= 67
RULE_async_funcdef	= 68
#else
#RULE_decorated_body	= 71
#endif
RULE_funcdefrettype	= 69
RULE_typedargslist	= 70
RULE_typedargslist_item	= 71
RULE_typedargslist_name	= 72
RULE_typedargslist_star	= 73
RULE_typedargslist_dbl_star	= 74
RULE_tfpdef	= 75
RULE_varargslist	= 76
RULE_varargslist_item	= 77
RULE_varargslist_name	= 78
RULE_varargslist_star	= 79
RULE_varargslist_dbl_star	= 80
RULE_vfpdef	= 81
RULE_stmt	= 82
RULE_simple_stmt	= 83
RULE_small_stmt	= 84
RULE_expr_stmt_2	= 85
RULE_expr_stmt_augassign	= 86
RULE_expr_stmt_assign_list	= 87
RULE_expr_stmt_assign	= 88
RULE_expr_stmt_6	= 89
RULE_testlist_star_expr_2	= 90
RULE_annassign	= 91
RULE_augassign	= 92
RULE_flow_stmt	= 93
RULE_raise_stmt_arg	= 94
RULE_raise_stmt_from	= 95
RULE_import_stmt	= 96
RULE_import_from_2	= 97
RULE_import_from_2b	= 98
RULE_import_from_3	= 99
RULE_import_as_names_paren	= 100
RULE_one_or_more_period_or_ellipsis	= 101
RULE_period_or_ellipsis	= 102
RULE_import_as_name	= 103
RULE_dotted_as_name	= 104
RULE_as_name	= 105
RULE_import_as_names	= 106
RULE_dotted_as_names	= 107
RULE_dotted_name	= 108
RULE_name_list	= 109
RULE_assert_stmt_extra	= 110
#if MICROPY_PY_ASYNC_AWAIT
RULE_compound_stmt	= 111
RULE_async_stmt_2	= 112
#else
#RULE_compound_stmt	= 116
#endif
RULE_if_stmt_elif_list	= 113
RULE_if_stmt_elif	= 114
RULE_try_stmt_2	= 115
RULE_try_stmt_except_and_more	= 116
RULE_try_stmt_except	= 117
RULE_try_stmt_as_name	= 118
RULE_try_stmt_except_list	= 119
RULE_try_stmt_finally	= 120
RULE_else_stmt	= 121
RULE_with_stmt_list	= 122
RULE_with_item	= 123
RULE_with_item_as	= 124
RULE_suite	= 125
RULE_suite_block	= 126
#if MICROPY_PY_ASSIGN_EXPR
RULE_namedexpr_test_2	= 127
#else
#RULE_namedexpr_test	= 132
#endif
RULE_test	= 128
RULE_test_if_else	= 129
RULE_test_nocond	= 130
RULE_not_test	= 131
RULE_comp_op	= 132
RULE_comp_op_not_in	= 133
RULE_comp_op_is	= 134
RULE_comp_op_is_not	= 135
RULE_shift_op	= 136
RULE_arith_op	= 137
RULE_term_op	= 138
RULE_factor	= 139
RULE_factor_op	= 140
#if MICROPY_PY_ASYNC_AWAIT
RULE_atom_expr	= 141
#else
#RULE_atom_expr	= 147
#endif
RULE_atom_expr_trailers	= 142
RULE_power_dbl_star	= 143
RULE_atom	= 144
RULE_atom_2b	= 145
RULE_testlist_comp	= 146
RULE_testlist_comp_2	= 147
RULE_testlist_comp_3	= 148
RULE_testlist_comp_3b	= 149
RULE_testlist_comp_3c	= 150
RULE_trailer	= 151
#if MICROPY_PY_BUILTINS_SLICE
RULE_subscript	= 152
RULE_subscript_3b	= 153
RULE_subscript_3c	= 154
RULE_subscript_3d	= 155
RULE_sliceop	= 156
#else
#endif
RULE_exprlist	= 157
RULE_exprlist_2	= 158
RULE_dictorsetmaker	= 159
#if MICROPY_PY_BUILTINS_SET
#else
#endif
RULE_dictorsetmaker_tail	= 160
RULE_dictorsetmaker_list	= 161
RULE_dictorsetmaker_list2	= 162
RULE_classdef_2	= 163
RULE_arglist	= 164
RULE_arglist_2	= 165
RULE_arglist_star	= 166
RULE_arglist_dbl_star	= 167
RULE_argument	= 168
#if MICROPY_PY_ASSIGN_EXPR
RULE_argument_2	= 169
RULE_argument_3	= 170
#else
#RULE_argument_2	= 177
#endif
RULE_comp_iter	= 171
RULE_comp_for	= 172
RULE_comp_if	= 173
RULE_yield_arg	= 174
RULE_yield_arg_from	= 175


rule_act_table:[uint8_t] = [
	(RULE_ACT_AND | 1 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_LIST | 2),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	#if MICROPY_PY_ASYNC_AWAIT
	#else
	#endif
	(RULE_ACT_AND | 8 | RULE_ACT_ADD_BLANK),
	(RULE_ACT_LIST | 3),
	(RULE_ACT_AND | 2),
	(RULE_ACT_LIST | 3),
	(RULE_ACT_AND | 2),
	(RULE_ACT_AND | 1),
	(RULE_ACT_AND | 1),
	(RULE_ACT_AND | 1),
	(RULE_ACT_AND | 2),
	(RULE_ACT_AND | 1),
	(RULE_ACT_AND | 2),
	(RULE_ACT_AND | 2),
	(RULE_ACT_AND | 4),
	(RULE_ACT_AND | 2),
	(RULE_ACT_AND | 2),
	(RULE_ACT_AND | 3),
	#if MICROPY_PY_ASYNC_AWAIT
	(RULE_ACT_AND | 2),
	#else
	#endif
	(RULE_ACT_AND | 6),
	(RULE_ACT_AND | 5),
	(RULE_ACT_AND | 7),
	(RULE_ACT_AND | 4),
	(RULE_ACT_AND | 4),
	(RULE_ACT_LIST | 2),
	#if MICROPY_PY_ASSIGN_EXPR
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	#else
	#endif
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_AND | 4 | RULE_ACT_ADD_BLANK),
	(RULE_ACT_AND | 4 | RULE_ACT_ADD_BLANK),
	(RULE_ACT_LIST | 1),
	(RULE_ACT_LIST | 1),
	(RULE_ACT_AND | 2),
	(RULE_ACT_LIST | 1),
	(RULE_ACT_AND | 2),
	(RULE_ACT_LIST | 1),
	(RULE_ACT_LIST | 1),
	(RULE_ACT_LIST | 1),
	(RULE_ACT_LIST | 1),
	(RULE_ACT_LIST | 1),
	(RULE_ACT_LIST | 1),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	#if MICROPY_PY_ASYNC_AWAIT
	(RULE_ACT_AND | 3),
	#else
	#endif
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_AND | 3),
	(RULE_ACT_AND | 3),
	(RULE_ACT_AND | 3),
	(RULE_ACT_AND | 3),
	(RULE_ACT_AND | 3),
	(RULE_ACT_AND | 2),
	#if MICROPY_PY_BUILTINS_SLICE
	(RULE_ACT_LIST | 3),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_AND | 2),
	#else
	#(RULE_ACT_LIST | 3),
	#endif
	(RULE_ACT_LIST | 3),
	#if MICROPY_PY_BUILTINS_SET
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	#else
	#(RULE_ACT_AND | 3),
	#endif
	(RULE_ACT_AND | 5 | RULE_ACT_ADD_BLANK),
	#if MICROPY_PY_ASSIGN_EXPR
	#else
	#endif
	(RULE_ACT_AND | 2),
	0,	# special node for a constant, generic Python object
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_OR | 3),
	(RULE_ACT_OR | 2),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_AND | 1),
	(RULE_ACT_AND | 4),
	(RULE_ACT_LIST | 2),
	#if MICROPY_PY_ASYNC_AWAIT
	(RULE_ACT_OR | 3),
	(RULE_ACT_AND | 2),
	#else
	#(RULE_ACT_OR | 2),
	#endif
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_LIST | 3),
	(RULE_ACT_OR | 3),
	(RULE_ACT_AND | 3 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_AND | 2),
	(RULE_ACT_AND | 3),
	(RULE_ACT_AND | 2),
	(RULE_ACT_LIST | 3),
	(RULE_ACT_OR | 3),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_AND | 2),
	(RULE_ACT_AND | 2),
	(RULE_ACT_AND | 1 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_OR | 2),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_OR | 8),
	(RULE_ACT_OR | 3),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_LIST | 2),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_OR | 2),
	(RULE_ACT_OR | 2),
	(RULE_ACT_AND | 3),
	(RULE_ACT_OR | 13),
	(RULE_ACT_OR | 5),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_OR | 2),
	(RULE_ACT_OR | 2),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_OR | 3),
	(RULE_ACT_AND | 3 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_LIST | 2),
	(RULE_ACT_OR | 2),
	(RULE_ACT_AND | 2),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_LIST | 3),
	(RULE_ACT_LIST | 1),
	(RULE_ACT_LIST | 1),
	(RULE_ACT_LIST | 1),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	#if MICROPY_PY_ASYNC_AWAIT
	(RULE_ACT_OR | 9),
	(RULE_ACT_OR | 3),
	#else
	#(RULE_ACT_OR | 8),
	#endif
	(RULE_ACT_LIST | 2),
	(RULE_ACT_AND | 4),
	(RULE_ACT_OR | 2),
	(RULE_ACT_AND | 3 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_AND | 4),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_LIST | 2),
	(RULE_ACT_AND | 3),
	(RULE_ACT_AND | 3 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_LIST | 1),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_OR | 2),
	(RULE_ACT_AND | 4 | RULE_ACT_ALLOW_IDENT),
	#if MICROPY_PY_ASSIGN_EXPR
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	#else
	#(RULE_ACT_OR | 1),
	#endif
	(RULE_ACT_OR | 2),
	(RULE_ACT_AND | 4),
	(RULE_ACT_OR | 2),
	(RULE_ACT_OR | 2),
	(RULE_ACT_OR | 9),
	(RULE_ACT_AND | 2),
	(RULE_ACT_AND | 2),
	(RULE_ACT_AND | 1),
	(RULE_ACT_OR | 2),
	(RULE_ACT_OR | 2),
	(RULE_ACT_OR | 5),
	(RULE_ACT_OR | 2),	#@FIXME: It said "rule(factor_2),"!
	(RULE_ACT_OR | 3),
	#if MICROPY_PY_ASYNC_AWAIT
	(RULE_ACT_OR | 2),
	#else
	#(RULE_ACT_OR | 1),
	#endif
	(RULE_ACT_LIST | 2),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_OR | 12),
	(RULE_ACT_OR | 2),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_OR | 2),
	(RULE_ACT_OR | 2),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_LIST | 3),
	(RULE_ACT_OR | 3),
	#if MICROPY_PY_BUILTINS_SLICE
	(RULE_ACT_OR | 2),
	(RULE_ACT_OR | 2),
	(RULE_ACT_AND | 2),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_AND | 2),
	#else
	#endif
	(RULE_ACT_LIST | 3),
	(RULE_ACT_OR | 2),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	#if MICROPY_PY_BUILTINS_SET
	#else
	#endif
	(RULE_ACT_OR | 2),
	(RULE_ACT_AND | 2),
	(RULE_ACT_LIST | 3),
	(RULE_ACT_AND | 3 | RULE_ACT_ALLOW_IDENT),
	(RULE_ACT_LIST | 3),
	(RULE_ACT_OR | 3),
	(RULE_ACT_AND | 2),
	(RULE_ACT_AND | 2),
	(RULE_ACT_AND | 2 | RULE_ACT_ALLOW_IDENT),
	#if MICROPY_PY_ASSIGN_EXPR
	(RULE_ACT_OR | 3),
	(RULE_ACT_AND | 2),
	#else
	#(RULE_ACT_OR | 2),
	#endif
	(RULE_ACT_OR | 2),
	(RULE_ACT_AND | 5 | RULE_ACT_ADD_BLANK),
	(RULE_ACT_AND | 3),
	(RULE_ACT_OR | 2),
	(RULE_ACT_AND | 2),
]

#static const uint16_t rule_arg_combined_table[]
rule_arg_combined_table:[uint16_t] = [
	(RULE_ARG_OPT_RULE | RULE_file_input_2),
	(RULE_ARG_RULE | RULE_file_input_3),
	(RULE_ARG_RULE | RULE_decorators), (RULE_ARG_RULE | RULE_decorated_body),
	#if MICROPY_PY_ASYNC_AWAIT
	#else
	#endif
	(RULE_ARG_TOK | MP_TOKEN_KW_DEF), (RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_OPEN), (RULE_ARG_OPT_RULE | RULE_typedargslist), (RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_CLOSE), (RULE_ARG_OPT_RULE | RULE_funcdefrettype), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite),
	(RULE_ARG_RULE | RULE_small_stmt), (RULE_ARG_TOK | MP_TOKEN_DEL_SEMICOLON),
	(RULE_ARG_RULE | RULE_testlist_star_expr), (RULE_ARG_OPT_RULE | RULE_expr_stmt_2),
	(RULE_ARG_RULE | RULE_testlist_star_expr_2), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
	(RULE_ARG_TOK | MP_TOKEN_KW_DEL), (RULE_ARG_RULE | RULE_exprlist),
	(RULE_ARG_TOK | MP_TOKEN_KW_PASS),
	(RULE_ARG_TOK | MP_TOKEN_KW_BREAK),
	(RULE_ARG_TOK | MP_TOKEN_KW_CONTINUE),
	(RULE_ARG_TOK | MP_TOKEN_KW_RETURN), (RULE_ARG_OPT_RULE | RULE_testlist),
	(RULE_ARG_RULE | RULE_yield_expr),
	(RULE_ARG_TOK | MP_TOKEN_KW_RAISE), (RULE_ARG_OPT_RULE | RULE_raise_stmt_arg),
	(RULE_ARG_TOK | MP_TOKEN_KW_IMPORT), (RULE_ARG_RULE | RULE_dotted_as_names),
	(RULE_ARG_TOK | MP_TOKEN_KW_FROM), (RULE_ARG_RULE | RULE_import_from_2), (RULE_ARG_TOK | MP_TOKEN_KW_IMPORT), (RULE_ARG_RULE | RULE_import_from_3),
	(RULE_ARG_TOK | MP_TOKEN_KW_GLOBAL), (RULE_ARG_RULE | RULE_name_list),
	(RULE_ARG_TOK | MP_TOKEN_KW_NONLOCAL), (RULE_ARG_RULE | RULE_name_list),
	(RULE_ARG_TOK | MP_TOKEN_KW_ASSERT), (RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_assert_stmt_extra),
	#if MICROPY_PY_ASYNC_AWAIT
	(RULE_ARG_TOK | MP_TOKEN_KW_ASYNC), (RULE_ARG_RULE | RULE_async_stmt_2),
	#else
	#endif
	(RULE_ARG_TOK | MP_TOKEN_KW_IF), (RULE_ARG_RULE | RULE_namedexpr_test), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite), (RULE_ARG_OPT_RULE | RULE_if_stmt_elif_list), (RULE_ARG_OPT_RULE | RULE_else_stmt),
	(RULE_ARG_TOK | MP_TOKEN_KW_WHILE), (RULE_ARG_RULE | RULE_namedexpr_test), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite), (RULE_ARG_OPT_RULE | RULE_else_stmt),
	(RULE_ARG_TOK | MP_TOKEN_KW_FOR), (RULE_ARG_RULE | RULE_exprlist), (RULE_ARG_TOK | MP_TOKEN_KW_IN), (RULE_ARG_RULE | RULE_testlist), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite), (RULE_ARG_OPT_RULE | RULE_else_stmt),
	(RULE_ARG_TOK | MP_TOKEN_KW_TRY), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite), (RULE_ARG_RULE | RULE_try_stmt_2),
	(RULE_ARG_TOK | MP_TOKEN_KW_WITH), (RULE_ARG_RULE | RULE_with_stmt_list), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite),
	(RULE_ARG_RULE | RULE_stmt),
	#if MICROPY_PY_ASSIGN_EXPR
	(RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_namedexpr_test_2),
	#else
	#endif
	(RULE_ARG_RULE | RULE_or_test), (RULE_ARG_OPT_RULE | RULE_test_if_else),
	(RULE_ARG_TOK | MP_TOKEN_KW_LAMBDA), (RULE_ARG_OPT_RULE | RULE_varargslist), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_test),
	(RULE_ARG_TOK | MP_TOKEN_KW_LAMBDA), (RULE_ARG_OPT_RULE | RULE_varargslist), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_test_nocond),
	(RULE_ARG_RULE | RULE_and_test), (RULE_ARG_TOK | MP_TOKEN_KW_OR),
	(RULE_ARG_RULE | RULE_not_test), (RULE_ARG_TOK | MP_TOKEN_KW_AND),
	(RULE_ARG_TOK | MP_TOKEN_KW_NOT), (RULE_ARG_RULE | RULE_not_test),
	(RULE_ARG_RULE | RULE_expr), (RULE_ARG_RULE | RULE_comp_op),
	(RULE_ARG_TOK | MP_TOKEN_OP_STAR), (RULE_ARG_RULE | RULE_expr),
	(RULE_ARG_RULE | RULE_xor_expr), (RULE_ARG_TOK | MP_TOKEN_OP_PIPE),
	(RULE_ARG_RULE | RULE_and_expr), (RULE_ARG_TOK | MP_TOKEN_OP_CARET),
	(RULE_ARG_RULE | RULE_shift_expr), (RULE_ARG_TOK | MP_TOKEN_OP_AMPERSAND),
	(RULE_ARG_RULE | RULE_arith_expr), (RULE_ARG_RULE | RULE_shift_op),
	(RULE_ARG_RULE | RULE_term), (RULE_ARG_RULE | RULE_arith_op),
	(RULE_ARG_RULE | RULE_factor), (RULE_ARG_RULE | RULE_term_op),
	(RULE_ARG_RULE | RULE_factor_op), (RULE_ARG_RULE | RULE_factor),
	(RULE_ARG_RULE | RULE_atom_expr), (RULE_ARG_OPT_RULE | RULE_power_dbl_star),
	#if MICROPY_PY_ASYNC_AWAIT
	(RULE_ARG_TOK | MP_TOKEN_KW_AWAIT), (RULE_ARG_RULE | RULE_atom), (RULE_ARG_OPT_RULE | RULE_atom_expr_trailers),
	#else
	#endif
	(RULE_ARG_RULE | RULE_atom), (RULE_ARG_OPT_RULE | RULE_atom_expr_trailers),
	(RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_OPEN), (RULE_ARG_OPT_RULE | RULE_atom_2b), (RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_CLOSE),
	(RULE_ARG_TOK | MP_TOKEN_DEL_BRACKET_OPEN), (RULE_ARG_OPT_RULE | RULE_testlist_comp), (RULE_ARG_TOK | MP_TOKEN_DEL_BRACKET_CLOSE),
	(RULE_ARG_TOK | MP_TOKEN_DEL_BRACE_OPEN), (RULE_ARG_OPT_RULE | RULE_dictorsetmaker), (RULE_ARG_TOK | MP_TOKEN_DEL_BRACE_CLOSE),
	(RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_OPEN), (RULE_ARG_OPT_RULE | RULE_arglist), (RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_CLOSE),
	(RULE_ARG_TOK | MP_TOKEN_DEL_BRACKET_OPEN), (RULE_ARG_RULE | RULE_subscriptlist), (RULE_ARG_TOK | MP_TOKEN_DEL_BRACKET_CLOSE),
	(RULE_ARG_TOK | MP_TOKEN_DEL_PERIOD), (RULE_ARG_TOK | MP_TOKEN_NAME),
	#if MICROPY_PY_BUILTINS_SLICE
	(RULE_ARG_RULE | RULE_subscript), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
	(RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_subscript_3),
	(RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_OPT_RULE | RULE_subscript_3b),
	#else
	#(RULE_ARG_RULE | RULE_test), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
	#endif
	(RULE_ARG_RULE | RULE_test), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
	#if MICROPY_PY_BUILTINS_SET
	(RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_generic_colon_test),
	#else
	#(RULE_ARG_RULE | RULE_test), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_test),
	#endif
	(RULE_ARG_TOK | MP_TOKEN_KW_CLASS), (RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_OPT_RULE | RULE_classdef_2), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite),
	#if MICROPY_PY_ASSIGN_EXPR
	#else
	#endif
	(RULE_ARG_TOK | MP_TOKEN_KW_YIELD), (RULE_ARG_OPT_RULE | RULE_yield_arg),
	(RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_test),
	(RULE_ARG_TOK | MP_TOKEN_DEL_EQUAL), (RULE_ARG_RULE | RULE_test),
	(RULE_ARG_TOK | MP_TOKEN_NEWLINE), (RULE_ARG_RULE | RULE_simple_stmt), (RULE_ARG_RULE | RULE_compound_stmt),
	(RULE_ARG_TOK | MP_TOKEN_NEWLINE), (RULE_ARG_RULE | RULE_stmt),
	(RULE_ARG_RULE | RULE_testlist), (RULE_ARG_OPT_RULE | RULE_eval_input_2),
	(RULE_ARG_TOK | MP_TOKEN_NEWLINE),
	(RULE_ARG_TOK | MP_TOKEN_OP_AT), (RULE_ARG_RULE | RULE_dotted_name), (RULE_ARG_OPT_RULE | RULE_trailer_paren), (RULE_ARG_TOK | MP_TOKEN_NEWLINE),
	(RULE_ARG_RULE | RULE_decorator),
	#if MICROPY_PY_ASYNC_AWAIT
	(RULE_ARG_RULE | RULE_classdef), (RULE_ARG_RULE | RULE_funcdef), (RULE_ARG_RULE | RULE_async_funcdef),
	(RULE_ARG_TOK | MP_TOKEN_KW_ASYNC), (RULE_ARG_RULE | RULE_funcdef),
	#else
	#(RULE_ARG_RULE | RULE_classdef), (RULE_ARG_RULE | RULE_funcdef),
	#endif
	(RULE_ARG_TOK | MP_TOKEN_DEL_MINUS_MORE), (RULE_ARG_RULE | RULE_test),
	(RULE_ARG_RULE | RULE_typedargslist_item), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
	(RULE_ARG_RULE | RULE_typedargslist_name), (RULE_ARG_RULE | RULE_typedargslist_star), (RULE_ARG_RULE | RULE_typedargslist_dbl_star),
	(RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_OPT_RULE | RULE_generic_colon_test), (RULE_ARG_OPT_RULE | RULE_generic_equal_test),
	(RULE_ARG_TOK | MP_TOKEN_OP_STAR), (RULE_ARG_OPT_RULE | RULE_tfpdef),
	(RULE_ARG_TOK | MP_TOKEN_OP_DBL_STAR), (RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_OPT_RULE | RULE_generic_colon_test),
	(RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_OPT_RULE | RULE_generic_colon_test),
	(RULE_ARG_RULE | RULE_varargslist_item), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
	(RULE_ARG_RULE | RULE_varargslist_name), (RULE_ARG_RULE | RULE_varargslist_star), (RULE_ARG_RULE | RULE_varargslist_dbl_star),
	(RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_OPT_RULE | RULE_generic_equal_test),
	(RULE_ARG_TOK | MP_TOKEN_OP_STAR), (RULE_ARG_OPT_RULE | RULE_vfpdef),
	(RULE_ARG_TOK | MP_TOKEN_OP_DBL_STAR), (RULE_ARG_TOK | MP_TOKEN_NAME),
	(RULE_ARG_TOK | MP_TOKEN_NAME),
	(RULE_ARG_RULE | RULE_compound_stmt), (RULE_ARG_RULE | RULE_simple_stmt),
	(RULE_ARG_RULE | RULE_simple_stmt_2), (RULE_ARG_TOK | MP_TOKEN_NEWLINE),
	
	#@FIXME: It said "rule(assert_stmt), rule(expr_stmt)"
	#(RULE_ARG_RULE | RULE_del_stmt), (RULE_ARG_RULE | RULE_pass_stmt), (RULE_ARG_RULE | RULE_flow_stmt), (RULE_ARG_RULE | RULE_import_stmt), (RULE_ARG_RULE | RULE_global_stmt), (RULE_ARG_RULE | RULE_nonlocal_stmt), rule(assert_stmt), rule(expr_stmt),
	(RULE_ARG_RULE | RULE_del_stmt), (RULE_ARG_RULE | RULE_pass_stmt), (RULE_ARG_RULE | RULE_flow_stmt), (RULE_ARG_RULE | RULE_import_stmt), (RULE_ARG_RULE | RULE_global_stmt), (RULE_ARG_RULE | RULE_nonlocal_stmt), (RULE_ARG_RULE | RULE_assert_stmt), (RULE_ARG_RULE | RULE_expr_stmt),
	
	(RULE_ARG_RULE | RULE_annassign), (RULE_ARG_RULE | RULE_expr_stmt_augassign), (RULE_ARG_RULE | RULE_expr_stmt_assign_list),
	(RULE_ARG_RULE | RULE_augassign), (RULE_ARG_RULE | RULE_expr_stmt_6),
	(RULE_ARG_RULE | RULE_expr_stmt_assign),
	(RULE_ARG_TOK | MP_TOKEN_DEL_EQUAL), (RULE_ARG_RULE | RULE_expr_stmt_6),
	(RULE_ARG_RULE | RULE_yield_expr), (RULE_ARG_RULE | RULE_testlist_star_expr),
	(RULE_ARG_RULE | RULE_star_expr), (RULE_ARG_RULE | RULE_test),
	(RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_expr_stmt_assign),
	
	#@FIXME: It said "tok(DEL_AMPERSAND_EQUAL), tok(DEL_PIPE_EQUAL), tok(DEL_CARET_EQUAL), tok(DEL_DBL_LESS_EQUAL), tok(DEL_DBL_MORE_EQUAL), tok(DEL_DBL_STAR_EQUAL), tok(DEL_DBL_SLASH_EQUAL)"
	#(RULE_ARG_TOK | MP_TOKEN_DEL_PLUS_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_MINUS_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_STAR_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_AT_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_SLASH_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_PERCENT_EQUAL), tok(DEL_AMPERSAND_EQUAL), tok(DEL_PIPE_EQUAL), tok(DEL_CARET_EQUAL), tok(DEL_DBL_LESS_EQUAL), tok(DEL_DBL_MORE_EQUAL), tok(DEL_DBL_STAR_EQUAL), tok(DEL_DBL_SLASH_EQUAL),
	(RULE_ARG_TOK | MP_TOKEN_DEL_PLUS_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_MINUS_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_STAR_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_AT_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_SLASH_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_PERCENT_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_AMPERSAND_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_PIPE_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_CARET_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_DBL_LESS_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_DBL_MORE_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_DBL_STAR_EQUAL), (RULE_ARG_TOK | MP_TOKEN_DEL_DBL_SLASH_EQUAL),
	
	(RULE_ARG_RULE | RULE_break_stmt), (RULE_ARG_RULE | RULE_continue_stmt), (RULE_ARG_RULE | RULE_return_stmt), (RULE_ARG_RULE | RULE_raise_stmt), (RULE_ARG_RULE | RULE_yield_stmt),
	(RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_raise_stmt_from),
	(RULE_ARG_TOK | MP_TOKEN_KW_FROM), (RULE_ARG_RULE | RULE_test),
	(RULE_ARG_RULE | RULE_import_name), (RULE_ARG_RULE | RULE_import_from),
	(RULE_ARG_RULE | RULE_dotted_name), (RULE_ARG_RULE | RULE_import_from_2b),
	(RULE_ARG_RULE | RULE_one_or_more_period_or_ellipsis), (RULE_ARG_OPT_RULE | RULE_dotted_name),
	(RULE_ARG_TOK | MP_TOKEN_OP_STAR), (RULE_ARG_RULE | RULE_import_as_names_paren), (RULE_ARG_RULE | RULE_import_as_names),
	(RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_OPEN), (RULE_ARG_RULE | RULE_import_as_names), (RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_CLOSE),
	(RULE_ARG_RULE | RULE_period_or_ellipsis),
	(RULE_ARG_TOK | MP_TOKEN_DEL_PERIOD), (RULE_ARG_TOK | MP_TOKEN_ELLIPSIS),
	(RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_OPT_RULE | RULE_as_name),
	(RULE_ARG_RULE | RULE_dotted_name), (RULE_ARG_OPT_RULE | RULE_as_name),
	(RULE_ARG_TOK | MP_TOKEN_KW_AS), (RULE_ARG_TOK | MP_TOKEN_NAME),
	(RULE_ARG_RULE | RULE_import_as_name), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
	(RULE_ARG_RULE | RULE_dotted_as_name), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
	(RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_TOK | MP_TOKEN_DEL_PERIOD),
	(RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
	(RULE_ARG_TOK | MP_TOKEN_DEL_COMMA), (RULE_ARG_RULE | RULE_test),
	#if MICROPY_PY_ASYNC_AWAIT
	
	#@FIXME: It said "rule(classdef), rule(decorated), rule(async_stmt)"
	#(RULE_ARG_RULE | RULE_if_stmt), (RULE_ARG_RULE | RULE_while_stmt), (RULE_ARG_RULE | RULE_for_stmt), (RULE_ARG_RULE | RULE_try_stmt), (RULE_ARG_RULE | RULE_with_stmt), (RULE_ARG_RULE | RULE_funcdef), rule(classdef), rule(decorated), rule(async_stmt),
	(RULE_ARG_RULE | RULE_if_stmt), (RULE_ARG_RULE | RULE_while_stmt), (RULE_ARG_RULE | RULE_for_stmt), (RULE_ARG_RULE | RULE_try_stmt), (RULE_ARG_RULE | RULE_with_stmt), (RULE_ARG_RULE | RULE_funcdef), (RULE_ARG_RULE | RULE_classdef), (RULE_ARG_RULE | RULE_decorated), (RULE_ARG_RULE | RULE_async_stmt),
	
	(RULE_ARG_RULE | RULE_funcdef), (RULE_ARG_RULE | RULE_with_stmt), (RULE_ARG_RULE | RULE_for_stmt),
	#else
	#(RULE_ARG_RULE | RULE_if_stmt), (RULE_ARG_RULE | RULE_while_stmt), (RULE_ARG_RULE | RULE_for_stmt), (RULE_ARG_RULE | RULE_try_stmt), (RULE_ARG_RULE | RULE_with_stmt), (RULE_ARG_RULE | RULE_funcdef), rule(classdef), rule(decorated),
	#endif
	(RULE_ARG_RULE | RULE_if_stmt_elif),
	(RULE_ARG_TOK | MP_TOKEN_KW_ELIF), (RULE_ARG_RULE | RULE_namedexpr_test), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite),
	(RULE_ARG_RULE | RULE_try_stmt_except_and_more), (RULE_ARG_RULE | RULE_try_stmt_finally),
	(RULE_ARG_RULE | RULE_try_stmt_except_list), (RULE_ARG_OPT_RULE | RULE_else_stmt), (RULE_ARG_OPT_RULE | RULE_try_stmt_finally),
	(RULE_ARG_TOK | MP_TOKEN_KW_EXCEPT), (RULE_ARG_OPT_RULE | RULE_try_stmt_as_name), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite),
	(RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_as_name),
	(RULE_ARG_RULE | RULE_try_stmt_except),
	(RULE_ARG_TOK | MP_TOKEN_KW_FINALLY), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite),
	(RULE_ARG_TOK | MP_TOKEN_KW_ELSE), (RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_RULE | RULE_suite),
	(RULE_ARG_RULE | RULE_with_item), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
	(RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_with_item_as),
	(RULE_ARG_TOK | MP_TOKEN_KW_AS), (RULE_ARG_RULE | RULE_expr),
	(RULE_ARG_RULE | RULE_suite_block), (RULE_ARG_RULE | RULE_simple_stmt),
	(RULE_ARG_TOK | MP_TOKEN_NEWLINE), (RULE_ARG_TOK | MP_TOKEN_INDENT), (RULE_ARG_RULE | RULE_suite_block_stmts), (RULE_ARG_TOK | MP_TOKEN_DEDENT),
	#if MICROPY_PY_ASSIGN_EXPR
	(RULE_ARG_TOK | MP_TOKEN_OP_ASSIGN), (RULE_ARG_RULE | RULE_test),
	#else
	#(RULE_ARG_RULE | RULE_test),
	#endif
	(RULE_ARG_RULE | RULE_lambdef), (RULE_ARG_RULE | RULE_test_if_expr),
	(RULE_ARG_TOK | MP_TOKEN_KW_IF), (RULE_ARG_RULE | RULE_or_test), (RULE_ARG_TOK | MP_TOKEN_KW_ELSE), (RULE_ARG_RULE | RULE_test),
	(RULE_ARG_RULE | RULE_lambdef_nocond), (RULE_ARG_RULE | RULE_or_test),
	(RULE_ARG_RULE | RULE_not_test_2), (RULE_ARG_RULE | RULE_comparison),
	
	#@FIXME: It said "tok(KW_IN)"
	#(RULE_ARG_TOK | MP_TOKEN_OP_LESS), (RULE_ARG_TOK | MP_TOKEN_OP_MORE), (RULE_ARG_TOK | MP_TOKEN_OP_DBL_EQUAL), (RULE_ARG_TOK | MP_TOKEN_OP_LESS_EQUAL), (RULE_ARG_TOK | MP_TOKEN_OP_MORE_EQUAL), (RULE_ARG_TOK | MP_TOKEN_OP_NOT_EQUAL), tok(KW_IN), (RULE_ARG_RULE | RULE_comp_op_not_in), (RULE_ARG_RULE | RULE_comp_op_is),
	(RULE_ARG_TOK | MP_TOKEN_OP_LESS), (RULE_ARG_TOK | MP_TOKEN_OP_MORE), (RULE_ARG_TOK | MP_TOKEN_OP_DBL_EQUAL), (RULE_ARG_TOK | MP_TOKEN_OP_LESS_EQUAL), (RULE_ARG_TOK | MP_TOKEN_OP_MORE_EQUAL), (RULE_ARG_TOK | MP_TOKEN_OP_NOT_EQUAL), (RULE_ARG_TOK | MP_TOKEN_KW_IN), (RULE_ARG_RULE | RULE_comp_op_not_in), (RULE_ARG_RULE | RULE_comp_op_is),
	
	(RULE_ARG_TOK | MP_TOKEN_KW_NOT), (RULE_ARG_TOK | MP_TOKEN_KW_IN),
	(RULE_ARG_TOK | MP_TOKEN_KW_IS), (RULE_ARG_OPT_RULE | RULE_comp_op_is_not),
	(RULE_ARG_TOK | MP_TOKEN_KW_NOT),
	(RULE_ARG_TOK | MP_TOKEN_OP_DBL_LESS), (RULE_ARG_TOK | MP_TOKEN_OP_DBL_MORE),
	(RULE_ARG_TOK | MP_TOKEN_OP_PLUS), (RULE_ARG_TOK | MP_TOKEN_OP_MINUS),
	(RULE_ARG_TOK | MP_TOKEN_OP_STAR), (RULE_ARG_TOK | MP_TOKEN_OP_AT), (RULE_ARG_TOK | MP_TOKEN_OP_SLASH), (RULE_ARG_TOK | MP_TOKEN_OP_PERCENT), (RULE_ARG_TOK | MP_TOKEN_OP_DBL_SLASH),
	(RULE_ARG_RULE | RULE_factor_2), (RULE_ARG_RULE | RULE_power),
	(RULE_ARG_TOK | MP_TOKEN_OP_PLUS), (RULE_ARG_TOK | MP_TOKEN_OP_MINUS), (RULE_ARG_TOK | MP_TOKEN_OP_TILDE),
	#if MICROPY_PY_ASYNC_AWAIT
	(RULE_ARG_RULE | RULE_atom_expr_await), (RULE_ARG_RULE | RULE_atom_expr_normal),
	#else
	#(RULE_ARG_RULE | RULE_atom_expr_normal),
	#endif
	(RULE_ARG_RULE | RULE_trailer),
	(RULE_ARG_TOK | MP_TOKEN_OP_DBL_STAR), (RULE_ARG_RULE | RULE_factor),
	
	#@FIXME: It said "tok(KW_TRUE), tok(KW_FALSE)"
	#(RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_TOK | MP_TOKEN_INTEGER), (RULE_ARG_TOK | MP_TOKEN_FLOAT_OR_IMAG), (RULE_ARG_TOK | MP_TOKEN_STRING), (RULE_ARG_TOK | MP_TOKEN_BYTES), (RULE_ARG_TOK | MP_TOKEN_ELLIPSIS), tok(KW_NONE), tok(KW_TRUE), tok(KW_FALSE), (RULE_ARG_RULE | RULE_atom_paren), (RULE_ARG_RULE | RULE_atom_bracket), (RULE_ARG_RULE | RULE_atom_brace),
	(RULE_ARG_TOK | MP_TOKEN_NAME), (RULE_ARG_TOK | MP_TOKEN_INTEGER), (RULE_ARG_TOK | MP_TOKEN_FLOAT_OR_IMAG), (RULE_ARG_TOK | MP_TOKEN_STRING), (RULE_ARG_TOK | MP_TOKEN_BYTES), (RULE_ARG_TOK | MP_TOKEN_ELLIPSIS), (RULE_ARG_TOK | MP_TOKEN_KW_NONE), (RULE_ARG_TOK | MP_TOKEN_KW_TRUE), (RULE_ARG_TOK | MP_TOKEN_KW_FALSE), (RULE_ARG_RULE | RULE_atom_paren), (RULE_ARG_RULE | RULE_atom_bracket), (RULE_ARG_RULE | RULE_atom_brace),
	
	(RULE_ARG_RULE | RULE_yield_expr), (RULE_ARG_RULE | RULE_testlist_comp),
	(RULE_ARG_RULE | RULE_testlist_comp_2), (RULE_ARG_OPT_RULE | RULE_testlist_comp_3),
	(RULE_ARG_RULE | RULE_star_expr), (RULE_ARG_RULE | RULE_namedexpr_test),
	(RULE_ARG_RULE | RULE_comp_for), (RULE_ARG_RULE | RULE_testlist_comp_3b),
	(RULE_ARG_TOK | MP_TOKEN_DEL_COMMA), (RULE_ARG_OPT_RULE | RULE_testlist_comp_3c),
	(RULE_ARG_RULE | RULE_testlist_comp_2), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
	(RULE_ARG_RULE | RULE_trailer_paren), (RULE_ARG_RULE | RULE_trailer_bracket), (RULE_ARG_RULE | RULE_trailer_period),
	#if MICROPY_PY_BUILTINS_SLICE
	(RULE_ARG_RULE | RULE_subscript_3), (RULE_ARG_RULE | RULE_subscript_2),
	(RULE_ARG_RULE | RULE_subscript_3c), (RULE_ARG_RULE | RULE_subscript_3d),
	(RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_OPT_RULE | RULE_test),
	(RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_sliceop),
	(RULE_ARG_TOK | MP_TOKEN_DEL_COLON), (RULE_ARG_OPT_RULE | RULE_test),
	#else
	#endif
	(RULE_ARG_RULE | RULE_exprlist_2), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
	(RULE_ARG_RULE | RULE_star_expr), (RULE_ARG_RULE | RULE_expr),
	(RULE_ARG_RULE | RULE_dictorsetmaker_item), (RULE_ARG_OPT_RULE | RULE_dictorsetmaker_tail),
	#if MICROPY_PY_BUILTINS_SET
	#else
	#endif
	(RULE_ARG_RULE | RULE_comp_for), (RULE_ARG_RULE | RULE_dictorsetmaker_list),
	(RULE_ARG_TOK | MP_TOKEN_DEL_COMMA), (RULE_ARG_OPT_RULE | RULE_dictorsetmaker_list2),
	(RULE_ARG_RULE | RULE_dictorsetmaker_item), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
	(RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_OPEN), (RULE_ARG_OPT_RULE | RULE_arglist), (RULE_ARG_TOK | MP_TOKEN_DEL_PAREN_CLOSE),
	(RULE_ARG_RULE | RULE_arglist_2), (RULE_ARG_TOK | MP_TOKEN_DEL_COMMA),
	(RULE_ARG_RULE | RULE_arglist_star), (RULE_ARG_RULE | RULE_arglist_dbl_star), (RULE_ARG_RULE | RULE_argument),
	(RULE_ARG_TOK | MP_TOKEN_OP_STAR), (RULE_ARG_RULE | RULE_test),
	(RULE_ARG_TOK | MP_TOKEN_OP_DBL_STAR), (RULE_ARG_RULE | RULE_test),
	(RULE_ARG_RULE | RULE_test), (RULE_ARG_OPT_RULE | RULE_argument_2),
	#if MICROPY_PY_ASSIGN_EXPR
	(RULE_ARG_RULE | RULE_comp_for), (RULE_ARG_RULE | RULE_generic_equal_test), (RULE_ARG_RULE | RULE_argument_3),
	(RULE_ARG_TOK | MP_TOKEN_OP_ASSIGN), (RULE_ARG_RULE | RULE_test),
	#else
	#(RULE_ARG_RULE | RULE_comp_for), (RULE_ARG_RULE | RULE_generic_equal_test),
	#endif
	(RULE_ARG_RULE | RULE_comp_for), (RULE_ARG_RULE | RULE_comp_if),
	(RULE_ARG_TOK | MP_TOKEN_KW_FOR), (RULE_ARG_RULE | RULE_exprlist), (RULE_ARG_TOK | MP_TOKEN_KW_IN), (RULE_ARG_RULE | RULE_or_test), (RULE_ARG_OPT_RULE | RULE_comp_iter),
	(RULE_ARG_TOK | MP_TOKEN_KW_IF), (RULE_ARG_RULE | RULE_test_nocond), (RULE_ARG_OPT_RULE | RULE_comp_iter),
	(RULE_ARG_RULE | RULE_yield_arg_from), (RULE_ARG_RULE | RULE_testlist),
	(RULE_ARG_TOK | MP_TOKEN_KW_FROM), (RULE_ARG_RULE | RULE_test),
]

#enum
# Fixed offsets with this script:
#	s = ...
#	o = 0
#	for l in s.split('\n'):
#		if l.strip() == '': continue
#		if l.startswith('#'):
#			print(l)
#			continue
#		#print(l)
#		name = l.split('=')[0].strip()
#		pad = int(name.split('_')[0][3:])
#		l2 = '%s = %d' % (name, o)
#		o += pad
#		print(l2)
PAD1_file_input = 0
PAD1_file_input_2 = 1
PAD2_decorated = 2
#if MICROPY_PY_ASYNC_AWAIT
#else
#endif
PAD8_funcdef = 4
PAD2_simple_stmt_2 = 12
PAD2_expr_stmt = 14
PAD2_testlist_star_expr = 16
PAD2_del_stmt = 18
PAD1_pass_stmt = 20
PAD1_break_stmt = 21
PAD1_continue_stmt = 22
PAD2_return_stmt = 23
PAD1_yield_stmt = 25
PAD2_raise_stmt = 26
PAD2_import_name = 28
PAD4_import_from = 30
PAD2_global_stmt = 34
PAD2_nonlocal_stmt = 36
PAD3_assert_stmt = 38
#if MICROPY_PY_ASYNC_AWAIT
PAD2_async_stmt = 41
#else
#endif
PAD6_if_stmt = 43
PAD5_while_stmt = 49
PAD7_for_stmt = 54
PAD4_try_stmt = 61
PAD4_with_stmt = 65
PAD1_suite_block_stmts = 69
#if MICROPY_PY_ASSIGN_EXPR
PAD2_namedexpr_test = 70
#else
#endif
PAD2_test_if_expr = 72
PAD4_lambdef = 74
PAD4_lambdef_nocond = 78
PAD2_or_test = 82
PAD2_and_test = 84
PAD2_not_test_2 = 86
PAD2_comparison = 88
PAD2_star_expr = 90
PAD2_expr = 92
PAD2_xor_expr = 94
PAD2_and_expr = 96
PAD2_shift_expr = 98
PAD2_arith_expr = 100
PAD2_term = 102
PAD2_factor_2 = 104
PAD2_power = 106
#if MICROPY_PY_ASYNC_AWAIT
PAD3_atom_expr_await = 108
#else
#endif
PAD2_atom_expr_normal = 111
PAD3_atom_paren = 113
PAD3_atom_bracket = 116
PAD3_atom_brace = 119
PAD3_trailer_paren = 122
PAD3_trailer_bracket = 125
PAD2_trailer_period = 128
#if MICROPY_PY_BUILTINS_SLICE
PAD2_subscriptlist = 130
PAD2_subscript_2 = 132
PAD2_subscript_3 = 134
#else
#PAD2_subscriptlist	= 54
#endif
PAD2_testlist = 136
#if MICROPY_PY_BUILTINS_SET
PAD2_dictorsetmaker_item = 138
#else
#PAD3_dictorsetmaker_item	= 57
#endif
PAD5_classdef = 140
#if MICROPY_PY_ASSIGN_EXPR
#else
#endif
PAD2_yield_expr = 145
# RULES have "const_object" here: special node for a constant, generic Python object
PAD2_generic_colon_test = 147
PAD2_generic_equal_test = 149
PAD3_single_input = 151
PAD2_file_input_3 = 154
PAD2_eval_input = 156
PAD1_eval_input_2 = 158
PAD4_decorator = 159
PAD1_decorators = 163
#if MICROPY_PY_ASYNC_AWAIT
PAD3_decorated_body = 164
PAD2_async_funcdef = 167
#else
#PAD2_decorated_body	= 70
#endif
PAD2_funcdefrettype = 169
PAD2_typedargslist = 171
PAD3_typedargslist_item = 173
PAD3_typedargslist_name = 176
PAD2_typedargslist_star = 179
PAD3_typedargslist_dbl_star = 181
PAD2_tfpdef = 184
PAD2_varargslist = 186
PAD3_varargslist_item = 188
PAD2_varargslist_name = 191
PAD2_varargslist_star = 193
PAD2_varargslist_dbl_star = 195
PAD1_vfpdef = 197
PAD2_stmt = 198
PAD2_simple_stmt = 200
PAD8_small_stmt = 202
PAD3_expr_stmt_2 = 210
PAD2_expr_stmt_augassign = 213
PAD1_expr_stmt_assign_list = 215
PAD2_expr_stmt_assign = 216
PAD2_expr_stmt_6 = 218
PAD2_testlist_star_expr_2 = 220
PAD3_annassign = 222
PAD13_augassign = 225
PAD5_flow_stmt = 238
PAD2_raise_stmt_arg = 243
PAD2_raise_stmt_from = 245
PAD2_import_stmt = 247
PAD2_import_from_2 = 249
PAD2_import_from_2b = 251
PAD3_import_from_3 = 253
PAD3_import_as_names_paren = 256
PAD1_one_or_more_period_or_ellipsis = 259
PAD2_period_or_ellipsis = 260
PAD2_import_as_name = 262
PAD2_dotted_as_name = 264
PAD2_as_name = 266
PAD2_import_as_names = 268
PAD2_dotted_as_names = 270
PAD2_dotted_name = 272
PAD2_name_list = 274
PAD2_assert_stmt_extra = 276
#if MICROPY_PY_ASYNC_AWAIT
PAD9_compound_stmt = 278
PAD3_async_stmt_2 = 287
#else
#PAD8_compound_stmt	= 115
#endif
PAD1_if_stmt_elif_list = 290
PAD4_if_stmt_elif = 291
PAD2_try_stmt_2 = 295
PAD3_try_stmt_except_and_more = 297
PAD4_try_stmt_except = 300
PAD2_try_stmt_as_name = 304
PAD1_try_stmt_except_list = 306
PAD3_try_stmt_finally = 307
PAD3_else_stmt = 310
PAD2_with_stmt_list = 313
PAD2_with_item = 315
PAD2_with_item_as = 317
PAD2_suite = 319
PAD4_suite_block = 321
#if MICROPY_PY_ASSIGN_EXPR
PAD2_namedexpr_test_2 = 325
#else
#PAD1_namedexpr_test	= 131
#endif
PAD2_test = 327
PAD4_test_if_else = 329
PAD2_test_nocond = 333
PAD2_not_test = 335
PAD9_comp_op = 337
PAD2_comp_op_not_in = 346
PAD2_comp_op_is = 348
PAD1_comp_op_is_not = 350
PAD2_shift_op = 351
PAD2_arith_op = 353
PAD5_term_op = 355
PAD2_factor = 360
PAD3_factor_op = 362
#if MICROPY_PY_ASYNC_AWAIT
PAD2_atom_expr = 365
#else
#PAD1_atom_expr	= 146
#endif
PAD1_atom_expr_trailers = 367
PAD2_power_dbl_star = 368
PAD12_atom = 370
PAD2_atom_2b = 382
PAD2_testlist_comp = 384
PAD2_testlist_comp_2 = 386
PAD2_testlist_comp_3 = 388
PAD2_testlist_comp_3b = 390
PAD2_testlist_comp_3c = 392
PAD3_trailer = 394
#if MICROPY_PY_BUILTINS_SLICE
PAD2_subscript = 397
PAD2_subscript_3b = 399
PAD2_subscript_3c = 401
PAD2_subscript_3d = 403
PAD2_sliceop = 405
#else
#endif
PAD2_exprlist = 407
PAD2_exprlist_2 = 409
PAD2_dictorsetmaker = 411
#if MICROPY_PY_BUILTINS_SET
#else
#endif
PAD2_dictorsetmaker_tail = 413
PAD2_dictorsetmaker_list = 415
PAD2_dictorsetmaker_list2 = 417
PAD3_classdef_2 = 419
PAD2_arglist = 422
PAD3_arglist_2 = 424
PAD2_arglist_star = 427
PAD2_arglist_dbl_star = 429
PAD2_argument = 431
#if MICROPY_PY_ASSIGN_EXPR
PAD3_argument_2 = 433
PAD2_argument_3 = 436
#else
#PAD2_argument_2	= 176
#endif
PAD2_comp_iter = 438
PAD5_comp_for = 440
PAD3_comp_if = 445
PAD2_yield_arg = 448
PAD2_yield_arg_from = 450


#static const uint8_t rule_arg_offset_table[]
rule_arg_offset_table:[uint8_t] = [
	PAD1_file_input & 0xff,
	PAD1_file_input_2 & 0xff,
	PAD2_decorated & 0xff,
	#if MICROPY_PY_ASYNC_AWAIT
	#else
	#endif
	PAD8_funcdef & 0xff,
	PAD2_simple_stmt_2 & 0xff,
	PAD2_expr_stmt & 0xff,
	PAD2_testlist_star_expr & 0xff,
	PAD2_del_stmt & 0xff,
	PAD1_pass_stmt & 0xff,
	PAD1_break_stmt & 0xff,
	PAD1_continue_stmt & 0xff,
	PAD2_return_stmt & 0xff,
	PAD1_yield_stmt & 0xff,
	PAD2_raise_stmt & 0xff,
	PAD2_import_name & 0xff,
	PAD4_import_from & 0xff,
	PAD2_global_stmt & 0xff,
	PAD2_nonlocal_stmt & 0xff,
	PAD3_assert_stmt & 0xff,
	#if MICROPY_PY_ASYNC_AWAIT
	PAD2_async_stmt & 0xff,
	#else
	#endif
	PAD6_if_stmt & 0xff,
	PAD5_while_stmt & 0xff,
	PAD7_for_stmt & 0xff,
	PAD4_try_stmt & 0xff,
	PAD4_with_stmt & 0xff,
	PAD1_suite_block_stmts & 0xff,
	#if MICROPY_PY_ASSIGN_EXPR
	PAD2_namedexpr_test & 0xff,
	#else
	#endif
	PAD2_test_if_expr & 0xff,
	PAD4_lambdef & 0xff,
	PAD4_lambdef_nocond & 0xff,
	PAD2_or_test & 0xff,
	PAD2_and_test & 0xff,
	PAD2_not_test_2 & 0xff,
	PAD2_comparison & 0xff,
	PAD2_star_expr & 0xff,
	PAD2_expr & 0xff,
	PAD2_xor_expr & 0xff,
	PAD2_and_expr & 0xff,
	PAD2_shift_expr & 0xff,
	PAD2_arith_expr & 0xff,
	PAD2_term & 0xff,
	PAD2_factor_2 & 0xff,
	PAD2_power & 0xff,
	#if MICROPY_PY_ASYNC_AWAIT
	PAD3_atom_expr_await & 0xff,
	#else
	#endif
	PAD2_atom_expr_normal & 0xff,
	PAD3_atom_paren & 0xff,
	PAD3_atom_bracket & 0xff,
	PAD3_atom_brace & 0xff,
	PAD3_trailer_paren & 0xff,
	PAD3_trailer_bracket & 0xff,
	PAD2_trailer_period & 0xff,
	#if MICROPY_PY_BUILTINS_SLICE
	PAD2_subscriptlist & 0xff,
	PAD2_subscript_2 & 0xff,
	PAD2_subscript_3 & 0xff,
	#else
	#PAD2_subscriptlist & 0xff,
	#endif
	PAD2_testlist & 0xff,
	#if MICROPY_PY_BUILTINS_SET
	PAD2_dictorsetmaker_item & 0xff,
	#else
	#PAD3_dictorsetmaker_item & 0xff,
	#endif
	PAD5_classdef & 0xff,
	#if MICROPY_PY_ASSIGN_EXPR
	#else
	#endif
	PAD2_yield_expr & 0xff,
	0,
	PAD2_generic_colon_test & 0xff,
	PAD2_generic_equal_test & 0xff,
	PAD3_single_input & 0xff,
	PAD2_file_input_3 & 0xff,
	PAD2_eval_input & 0xff,
	PAD1_eval_input_2 & 0xff,
	PAD4_decorator & 0xff,
	PAD1_decorators & 0xff,
	#if MICROPY_PY_ASYNC_AWAIT
	PAD3_decorated_body & 0xff,
	PAD2_async_funcdef & 0xff,
	#else
	#PAD2_decorated_body & 0xff,
	#endif
	PAD2_funcdefrettype & 0xff,
	PAD2_typedargslist & 0xff,
	PAD3_typedargslist_item & 0xff,
	PAD3_typedargslist_name & 0xff,
	PAD2_typedargslist_star & 0xff,
	PAD3_typedargslist_dbl_star & 0xff,
	PAD2_tfpdef & 0xff,
	PAD2_varargslist & 0xff,
	PAD3_varargslist_item & 0xff,
	PAD2_varargslist_name & 0xff,
	PAD2_varargslist_star & 0xff,
	PAD2_varargslist_dbl_star & 0xff,
	PAD1_vfpdef & 0xff,
	PAD2_stmt & 0xff,
	PAD2_simple_stmt & 0xff,
	PAD8_small_stmt & 0xff,
	PAD3_expr_stmt_2 & 0xff,
	PAD2_expr_stmt_augassign & 0xff,
	PAD1_expr_stmt_assign_list & 0xff,
	PAD2_expr_stmt_assign & 0xff,
	PAD2_expr_stmt_6 & 0xff,
	PAD2_testlist_star_expr_2 & 0xff,
	PAD3_annassign & 0xff,
	PAD13_augassign & 0xff,
	PAD5_flow_stmt & 0xff,
	PAD2_raise_stmt_arg & 0xff,
	PAD2_raise_stmt_from & 0xff,
	PAD2_import_stmt & 0xff,
	PAD2_import_from_2 & 0xff,
	PAD2_import_from_2b & 0xff,
	PAD3_import_from_3 & 0xff,
	PAD3_import_as_names_paren & 0xff,
	PAD1_one_or_more_period_or_ellipsis & 0xff,
	PAD2_period_or_ellipsis & 0xff,
	PAD2_import_as_name & 0xff,
	PAD2_dotted_as_name & 0xff,
	PAD2_as_name & 0xff,
	PAD2_import_as_names & 0xff,
	PAD2_dotted_as_names & 0xff,
	PAD2_dotted_name & 0xff,
	PAD2_name_list & 0xff,
	PAD2_assert_stmt_extra & 0xff,
	#if MICROPY_PY_ASYNC_AWAIT
	PAD9_compound_stmt & 0xff,
	PAD3_async_stmt_2 & 0xff,
	#else
	#PAD8_compound_stmt & 0xff,
	#endif
	PAD1_if_stmt_elif_list & 0xff,
	PAD4_if_stmt_elif & 0xff,
	PAD2_try_stmt_2 & 0xff,
	PAD3_try_stmt_except_and_more & 0xff,
	PAD4_try_stmt_except & 0xff,
	PAD2_try_stmt_as_name & 0xff,
	PAD1_try_stmt_except_list & 0xff,
	PAD3_try_stmt_finally & 0xff,
	PAD3_else_stmt & 0xff,
	PAD2_with_stmt_list & 0xff,
	PAD2_with_item & 0xff,
	PAD2_with_item_as & 0xff,
	PAD2_suite & 0xff,
	PAD4_suite_block & 0xff,
	#if MICROPY_PY_ASSIGN_EXPR
	PAD2_namedexpr_test_2 & 0xff,
	#else
	#PAD1_namedexpr_test & 0xff,
	#endif
	PAD2_test & 0xff,
	PAD4_test_if_else & 0xff,
	PAD2_test_nocond & 0xff,
	PAD2_not_test & 0xff,
	PAD9_comp_op & 0xff,
	PAD2_comp_op_not_in & 0xff,
	PAD2_comp_op_is & 0xff,
	PAD1_comp_op_is_not & 0xff,
	PAD2_shift_op & 0xff,
	PAD2_arith_op & 0xff,
	PAD5_term_op & 0xff,
	PAD2_factor & 0xff,
	PAD3_factor_op & 0xff,
	#if MICROPY_PY_ASYNC_AWAIT
	PAD2_atom_expr & 0xff,
	#else
	#PAD1_atom_expr & 0xff,
	#endif
	PAD1_atom_expr_trailers & 0xff,
	PAD2_power_dbl_star & 0xff,
	PAD12_atom & 0xff,
	PAD2_atom_2b & 0xff,
	PAD2_testlist_comp & 0xff,
	PAD2_testlist_comp_2 & 0xff,
	PAD2_testlist_comp_3 & 0xff,
	PAD2_testlist_comp_3b & 0xff,
	PAD2_testlist_comp_3c & 0xff,
	PAD3_trailer & 0xff,
	#if MICROPY_PY_BUILTINS_SLICE
	PAD2_subscript & 0xff,
	PAD2_subscript_3b & 0xff,
	PAD2_subscript_3c & 0xff,
	PAD2_subscript_3d & 0xff,
	PAD2_sliceop & 0xff,
	#else
	#endif
	PAD2_exprlist & 0xff,
	PAD2_exprlist_2 & 0xff,
	PAD2_dictorsetmaker & 0xff,
	#if MICROPY_PY_BUILTINS_SET
	#else
	#endif
	PAD2_dictorsetmaker_tail & 0xff,
	PAD2_dictorsetmaker_list & 0xff,
	PAD2_dictorsetmaker_list2 & 0xff,
	PAD3_classdef_2 & 0xff,
	PAD2_arglist & 0xff,
	PAD3_arglist_2 & 0xff,
	PAD2_arglist_star & 0xff,
	PAD2_arglist_dbl_star & 0xff,
	PAD2_argument & 0xff,
	#if MICROPY_PY_ASSIGN_EXPR
	PAD3_argument_2 & 0xff,
	PAD2_argument_3 & 0xff,
	#else
	#PAD2_argument_2 & 0xff,
	#endif
	PAD2_comp_iter & 0xff,
	PAD5_comp_for & 0xff,
	PAD3_comp_if & 0xff,
	PAD2_yield_arg & 0xff,
	PAD2_yield_arg_from & 0xff,
]

#@FIXME: This checks all "PADx_xxx" if it is >= 0x100. If it is, it is set to the first "RULE_xxx"
# e.g. = (PAD2_yield_arg >= 0x100 ? RULE_yield_arg : 0)
FIRST_RULE_WITH_OFFSET_ABOVE_255 = RULE_import_as_names_paren

#if MICROPY_DEBUG_PARSE_RULE_NAME
#static const char *const rule_name_table[]
rule_name_table:[str] = [
	"file_input",
	"file_input_2",
	"decorated",
	#if MICROPY_PY_ASYNC_AWAIT
	#else
	#endif
	"funcdef",
	"simple_stmt_2",
	"expr_stmt",
	"testlist_star_expr",
	"del_stmt",
	"pass_stmt",
	"break_stmt",
	"continue_stmt",
	"return_stmt",
	"yield_stmt",
	"raise_stmt",
	"import_name",
	"import_from",
	"global_stmt",
	"nonlocal_stmt",
	"assert_stmt",
	#if MICROPY_PY_ASYNC_AWAIT
	"async_stmt",
	#else
	#endif
	"if_stmt",
	"while_stmt",
	"for_stmt",
	"try_stmt",
	"with_stmt",
	"suite_block_stmts",
	#if MICROPY_PY_ASSIGN_EXPR
	"namedexpr_test",
	#else
	#endif
	"test_if_expr",
	"lambdef",
	"lambdef_nocond",
	"or_test",
	"and_test",
	"not_test_2",
	"comparison",
	"star_expr",
	"expr",
	"xor_expr",
	"and_expr",
	"shift_expr",
	"arith_expr",
	"term",
	"factor_2",
	"power",
	#if MICROPY_PY_ASYNC_AWAIT
	"atom_expr_await",
	#else
	#endif
	"atom_expr_normal",
	"atom_paren",
	"atom_bracket",
	"atom_brace",
	"trailer_paren",
	"trailer_bracket",
	"trailer_period",
	#if MICROPY_PY_BUILTINS_SLICE
	"subscriptlist",
	"subscript_2",
	"subscript_3",
	#else
	#"subscriptlist",
	#endif
	"testlist",
	#if MICROPY_PY_BUILTINS_SET
	"dictorsetmaker_item",
	#else
	#"dictorsetmaker_item",
	#endif
	"classdef",
	#if MICROPY_PY_ASSIGN_EXPR
	#else
	#endif
	"yield_expr",
	"",
	"generic_colon_test",
	"generic_equal_test",
	"single_input",
	"file_input_3",
	"eval_input",
	"eval_input_2",
	"decorator",
	"decorators",
	#if MICROPY_PY_ASYNC_AWAIT
	"decorated_body",
	"async_funcdef",
	#else
	#"decorated_body",
	#endif
	"funcdefrettype",
	"typedargslist",
	"typedargslist_item",
	"typedargslist_name",
	"typedargslist_star",
	"typedargslist_dbl_star",
	"tfpdef",
	"varargslist",
	"varargslist_item",
	"varargslist_name",
	"varargslist_star",
	"varargslist_dbl_star",
	"vfpdef",
	"stmt",
	"simple_stmt",
	"small_stmt",
	"expr_stmt_2",
	"expr_stmt_augassign",
	"expr_stmt_assign_list",
	"expr_stmt_assign",
	"expr_stmt_6",
	"testlist_star_expr_2",
	"annassign",
	"augassign",
	"flow_stmt",
	"raise_stmt_arg",
	"raise_stmt_from",
	"import_stmt",
	"import_from_2",
	"import_from_2b",
	"import_from_3",
	"import_as_names_paren",
	"one_or_more_period_or_ellipsis",
	"period_or_ellipsis",
	"import_as_name",
	"dotted_as_name",
	"as_name",
	"import_as_names",
	"dotted_as_names",
	"dotted_name",
	"name_list",
	"assert_stmt_extra",
	#if MICROPY_PY_ASYNC_AWAIT
	"compound_stmt",
	"async_stmt_2",
	#else
	#"compound_stmt",
	#endif
	"if_stmt_elif_list",
	"if_stmt_elif",
	"try_stmt_2",
	"try_stmt_except_and_more",
	"try_stmt_except",
	"try_stmt_as_name",
	"try_stmt_except_list",
	"try_stmt_finally",
	"else_stmt",
	"with_stmt_list",
	"with_item",
	"with_item_as",
	"suite",
	"suite_block",
	#if MICROPY_PY_ASSIGN_EXPR
	"namedexpr_test_2",
	#else
	#"namedexpr_test",
	#endif
	"test",
	"test_if_else",
	"test_nocond",
	"not_test",
	"comp_op",
	"comp_op_not_in",
	"comp_op_is",
	"comp_op_is_not",
	"shift_op",
	"arith_op",
	"term_op",
	"factor",
	"factor_op",
	#if MICROPY_PY_ASYNC_AWAIT
	"atom_expr",
	#else
	#"atom_expr",
	#endif
	"atom_expr_trailers",
	"power_dbl_star",
	"atom",
	"atom_2b",
	"testlist_comp",
	"testlist_comp_2",
	"testlist_comp_3",
	"testlist_comp_3b",
	"testlist_comp_3c",
	"trailer",
	#if MICROPY_PY_BUILTINS_SLICE
	"subscript",
	"subscript_3b",
	"subscript_3c",
	"subscript_3d",
	"sliceop",
	#else
	#endif
	"exprlist",
	"exprlist_2",
	"dictorsetmaker",
	#if MICROPY_PY_BUILTINS_SET
	#else
	#endif
	"dictorsetmaker_tail",
	"dictorsetmaker_list",
	"dictorsetmaker_list2",
	"classdef_2",
	"arglist",
	"arglist_2",
	"arglist_star",
	"arglist_dbl_star",
	"argument",
	#if MICROPY_PY_ASSIGN_EXPR
	"argument_2",
	"argument_3",
	#else
	#"argument_2",
	#endif
	"comp_iter",
	"comp_for",
	"comp_if",
	"yield_arg",
	"yield_arg_from",
]

if __name__ == '__main__':
	rule_id = RULE_yield_arg_from
	print('rule_id=%d' % rule_id)
	print('rule_name="%s"' % rule_name_table[rule_id])
	o = rule_arg_offset_table[rule_id] + 0x100 if rule_id >= FIRST_RULE_WITH_OFFSET_ABOVE_255 else 0
	print('rule_act=%d' % rule_act_table[rule_id])
	print('rule_arg=%s...' % ', '.join([ '0x%04X'%a for a in rule_arg_combined_table[o:o+6] ]))
	print('rule_arg_offset=%d' % o)
	print('PAD=%d' % PAD2_yield_arg_from)

