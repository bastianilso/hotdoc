/* Generated by re2c 0.16 */
/*
 * re2c syntax scanner for gtk-doc
 *
 * Copyright 2016 Mathieu Duponchelle <mathieu.duponchelle@opencredd.com>
 * Copyright 2016 Collabora Ltd.
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
 */

#include <stdlib.h>
#include <string.h>
#include "cmark_gtkdoc_scanner.h"

cmark_bufsize_t _ext_scan_at(cmark_bufsize_t (*scanner)(const unsigned char *),
	const char *s, cmark_bufsize_t offset)
{
	cmark_bufsize_t res;
	cmark_bufsize_t len = strlen(s);
	unsigned char *ptr = (unsigned char *)s;

        if (ptr == NULL || offset > len) {
          return 0;
        } else {
	  res = scanner(ptr + offset);
        }

	return res;
}



// Scan an opening gtk-doc code block.
cmark_bufsize_t _scan_open_gtkdoc_code_block(const unsigned char *p)
{
  const unsigned char *marker = NULL;
  const unsigned char *start = p;

{
	unsigned char yych;
	yych = *(marker = p);
	if (yych <= 0xDF) {
		if (yych <= '{') {
			if (yych != '\n') goto yy3;
		} else {
			if (yych <= '|') goto yy4;
			if (yych <= 0x7F) goto yy3;
			if (yych >= 0xC2) goto yy5;
		}
	} else {
		if (yych <= 0xEF) {
			if (yych <= 0xE0) goto yy7;
			if (yych == 0xED) goto yy9;
			goto yy8;
		} else {
			if (yych <= 0xF0) goto yy10;
			if (yych <= 0xF3) goto yy11;
			if (yych <= 0xF4) goto yy12;
		}
	}
yy2:
	{ return 0; }
yy3:
	yych = *++p;
	goto yy2;
yy4:
	yych = *++p;
	if (yych == '[') goto yy13;
	goto yy2;
yy5:
	yych = *++p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0xBF) goto yy3;
yy6:
	p = marker;
	goto yy2;
yy7:
	yych = *++p;
	if (yych <= 0x9F) goto yy6;
	if (yych <= 0xBF) goto yy5;
	goto yy6;
yy8:
	yych = *++p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0xBF) goto yy5;
	goto yy6;
yy9:
	yych = *++p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0x9F) goto yy5;
	goto yy6;
yy10:
	yych = *++p;
	if (yych <= 0x8F) goto yy6;
	if (yych <= 0xBF) goto yy8;
	goto yy6;
yy11:
	yych = *++p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0xBF) goto yy8;
	goto yy6;
yy12:
	yych = *++p;
	if (yych <= 0x7F) goto yy6;
	if (yych <= 0x8F) goto yy8;
	goto yy6;
yy13:
	++p;
	{ return (cmark_bufsize_t)(p - start); }
}

}

// Scan a language comment
cmark_bufsize_t _scan_language_comment(const unsigned char *p)
{
  const unsigned char *marker = NULL;
  const unsigned char *start = p;

{
	unsigned char yych;
	static const unsigned char yybm[] = {
		  0,  32,  32,  32,  32,  32,  32,  32, 
		 32, 160,   0,  32,  32,   0,  32,  32, 
		 32,  32,  32,  32,  32,  32,  32,  32, 
		 32,  32,  32,  32,  32,  32,  32,  32, 
		 64,  32,  32,  32,  32,  32,  32,  32, 
		 32,  32,  32,  32,  32,  32,  32,  32, 
		 32,  32,  32,  32,  32,  32,  32,  32, 
		 32,  32,  32,  32,  32,  32,  32,  32, 
		 32,  32,  32,  32,  32,  32,  32,  32, 
		 32,  32,  32,  32,  32,  32,  32,  32, 
		 32,  32,  32,  32,  32,  32,  32,  32, 
		 32,  32,  32,  32,  32,  32,  32,  32, 
		  0,  32,  32,  32,  32,  32,  32,  32, 
		 32,  32,  32,  32,  32,  32,  32,  32, 
		 32,  32,  32,  32,  32,  32,  32,  32, 
		 32,  32,  32,  32,  32,  32,  32,  32, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
		  0,   0,   0,   0,   0,   0,   0,   0, 
	};
	yych = *(marker = p);
	if (yych <= 0xDF) {
		if (yych <= ';') {
			if (yych != '\n') goto yy18;
		} else {
			if (yych <= '<') goto yy19;
			if (yych <= 0x7F) goto yy18;
			if (yych >= 0xC2) goto yy20;
		}
	} else {
		if (yych <= 0xEF) {
			if (yych <= 0xE0) goto yy22;
			if (yych == 0xED) goto yy24;
			goto yy23;
		} else {
			if (yych <= 0xF0) goto yy25;
			if (yych <= 0xF3) goto yy26;
			if (yych <= 0xF4) goto yy27;
		}
	}
yy17:
	{ return 0; }
yy18:
	yych = *++p;
	goto yy17;
yy19:
	yych = *(marker = ++p);
	if (yych == '!') goto yy28;
	goto yy17;
yy20:
	yych = *++p;
	if (yych <= 0x7F) goto yy21;
	if (yych <= 0xBF) goto yy18;
yy21:
	p = marker;
	goto yy17;
yy22:
	yych = *++p;
	if (yych <= 0x9F) goto yy21;
	if (yych <= 0xBF) goto yy20;
	goto yy21;
yy23:
	yych = *++p;
	if (yych <= 0x7F) goto yy21;
	if (yych <= 0xBF) goto yy20;
	goto yy21;
yy24:
	yych = *++p;
	if (yych <= 0x7F) goto yy21;
	if (yych <= 0x9F) goto yy20;
	goto yy21;
yy25:
	yych = *++p;
	if (yych <= 0x8F) goto yy21;
	if (yych <= 0xBF) goto yy23;
	goto yy21;
yy26:
	yych = *++p;
	if (yych <= 0x7F) goto yy21;
	if (yych <= 0xBF) goto yy23;
	goto yy21;
yy27:
	yych = *++p;
	if (yych <= 0x7F) goto yy21;
	if (yych <= 0x8F) goto yy23;
	goto yy21;
yy28:
	yych = *++p;
	if (yych != '-') goto yy21;
	yych = *++p;
	if (yych != '-') goto yy21;
	yych = *++p;
	if (yych != ' ') goto yy21;
	yych = *++p;
	if (yych == 'L') goto yy32;
	if (yych != 'l') goto yy21;
yy32:
	yych = *++p;
	if (yych == 'A') goto yy33;
	if (yych != 'a') goto yy21;
yy33:
	yych = *++p;
	if (yych == 'N') goto yy34;
	if (yych != 'n') goto yy21;
yy34:
	yych = *++p;
	if (yych == 'G') goto yy35;
	if (yych != 'g') goto yy21;
yy35:
	yych = *++p;
	if (yych == 'U') goto yy36;
	if (yych != 'u') goto yy21;
yy36:
	yych = *++p;
	if (yych == 'A') goto yy37;
	if (yych != 'a') goto yy21;
yy37:
	yych = *++p;
	if (yych == 'G') goto yy38;
	if (yych != 'g') goto yy21;
yy38:
	yych = *++p;
	if (yych == 'E') goto yy39;
	if (yych != 'e') goto yy21;
yy39:
	yych = *++p;
	if (yych != '=') goto yy21;
	yych = *++p;
	if (yych != '"') goto yy21;
yy41:
	++p;
	yych = *p;
	if (yybm[0+yych] & 32) {
		goto yy41;
	}
	if (yych <= 0xEC) {
		if (yych <= 0xC1) {
			if (yych <= '\r') goto yy21;
			if (yych >= '!') goto yy21;
		} else {
			if (yych <= 0xDF) goto yy45;
			if (yych <= 0xE0) goto yy46;
			goto yy47;
		}
	} else {
		if (yych <= 0xF0) {
			if (yych <= 0xED) goto yy48;
			if (yych <= 0xEF) goto yy47;
			goto yy49;
		} else {
			if (yych <= 0xF3) goto yy50;
			if (yych <= 0xF4) goto yy51;
			goto yy21;
		}
	}
yy43:
	++p;
	yych = *p;
	if (yybm[0+yych] & 64) {
		goto yy43;
	}
	if (yych <= 0x7F) {
		if (yych <= '\r') {
			if (yych <= '\t') {
				if (yych <= 0x00) goto yy21;
				goto yy41;
			} else {
				if (yych <= '\n') goto yy21;
				if (yych <= '\f') goto yy41;
				goto yy21;
			}
		} else {
			if (yych <= '-') {
				if (yych <= ',') goto yy41;
				goto yy52;
			} else {
				if (yych == '`') goto yy21;
				goto yy41;
			}
		}
	} else {
		if (yych <= 0xED) {
			if (yych <= 0xDF) {
				if (yych <= 0xC1) goto yy21;
			} else {
				if (yych <= 0xE0) goto yy46;
				if (yych <= 0xEC) goto yy47;
				goto yy48;
			}
		} else {
			if (yych <= 0xF0) {
				if (yych <= 0xEF) goto yy47;
				goto yy49;
			} else {
				if (yych <= 0xF3) goto yy50;
				if (yych <= 0xF4) goto yy51;
				goto yy21;
			}
		}
	}
yy45:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy21;
	if (yych <= 0xBF) goto yy41;
	goto yy21;
yy46:
	++p;
	yych = *p;
	if (yych <= 0x9F) goto yy21;
	if (yych <= 0xBF) goto yy45;
	goto yy21;
yy47:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy21;
	if (yych <= 0xBF) goto yy45;
	goto yy21;
yy48:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy21;
	if (yych <= 0x9F) goto yy45;
	goto yy21;
yy49:
	++p;
	yych = *p;
	if (yych <= 0x8F) goto yy21;
	if (yych <= 0xBF) goto yy47;
	goto yy21;
yy50:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy21;
	if (yych <= 0xBF) goto yy47;
	goto yy21;
yy51:
	++p;
	yych = *p;
	if (yych <= 0x7F) goto yy21;
	if (yych <= 0x8F) goto yy47;
	goto yy21;
yy52:
	++p;
	yych = *p;
	if (yybm[0+yych] & 64) {
		goto yy43;
	}
	if (yych <= 0x7F) {
		if (yych <= '\r') {
			if (yych <= '\t') {
				if (yych <= 0x00) goto yy21;
				goto yy41;
			} else {
				if (yych <= '\n') goto yy21;
				if (yych <= '\f') goto yy41;
				goto yy21;
			}
		} else {
			if (yych <= '-') {
				if (yych <= ',') goto yy41;
			} else {
				if (yych == '`') goto yy21;
				goto yy41;
			}
		}
	} else {
		if (yych <= 0xED) {
			if (yych <= 0xDF) {
				if (yych <= 0xC1) goto yy21;
				goto yy45;
			} else {
				if (yych <= 0xE0) goto yy46;
				if (yych <= 0xEC) goto yy47;
				goto yy48;
			}
		} else {
			if (yych <= 0xF0) {
				if (yych <= 0xEF) goto yy47;
				goto yy49;
			} else {
				if (yych <= 0xF3) goto yy50;
				if (yych <= 0xF4) goto yy51;
				goto yy21;
			}
		}
	}
	++p;
	yych = *p;
	if (yybm[0+yych] & 64) {
		goto yy43;
	}
	if (yych <= 0x7F) {
		if (yych <= '\r') {
			if (yych <= '\t') {
				if (yych <= 0x00) goto yy21;
				goto yy41;
			} else {
				if (yych <= '\n') goto yy21;
				if (yych <= '\f') goto yy41;
				goto yy21;
			}
		} else {
			if (yych <= '>') {
				if (yych <= '=') goto yy41;
			} else {
				if (yych == '`') goto yy21;
				goto yy41;
			}
		}
	} else {
		if (yych <= 0xED) {
			if (yych <= 0xDF) {
				if (yych <= 0xC1) goto yy21;
				goto yy45;
			} else {
				if (yych <= 0xE0) goto yy46;
				if (yych <= 0xEC) goto yy47;
				goto yy48;
			}
		} else {
			if (yych <= 0xF0) {
				if (yych <= 0xEF) goto yy47;
				goto yy49;
			} else {
				if (yych <= 0xF3) goto yy50;
				if (yych <= 0xF4) goto yy51;
				goto yy21;
			}
		}
	}
	++p;
	yych = *p;
	marker = p;
	if (yybm[0+yych] & 128) {
		goto yy55;
	}
	if (yych <= 0x7F) {
		if (yych <= '\r') {
			if (yych <= 0x08) {
				if (yych <= 0x00) goto yy21;
				goto yy41;
			} else {
				if (yych <= '\n') goto yy57;
				if (yych <= '\f') goto yy41;
				goto yy57;
			}
		} else {
			if (yych <= ' ') {
				if (yych <= 0x1F) goto yy41;
				goto yy59;
			} else {
				if (yych == '`') goto yy21;
				goto yy41;
			}
		}
	} else {
		if (yych <= 0xED) {
			if (yych <= 0xDF) {
				if (yych <= 0xC1) goto yy21;
				goto yy45;
			} else {
				if (yych <= 0xE0) goto yy46;
				if (yych <= 0xEC) goto yy47;
				goto yy48;
			}
		} else {
			if (yych <= 0xF0) {
				if (yych <= 0xEF) goto yy47;
				goto yy49;
			} else {
				if (yych <= 0xF3) goto yy50;
				if (yych <= 0xF4) goto yy51;
				goto yy21;
			}
		}
	}
yy55:
	++p;
	yych = *p;
	if (yybm[0+yych] & 128) {
		goto yy55;
	}
	if (yych <= 0x7F) {
		if (yych <= '\r') {
			if (yych <= 0x08) {
				if (yych <= 0x00) goto yy21;
				goto yy41;
			} else {
				if (yych <= '\n') goto yy57;
				if (yych <= '\f') goto yy41;
			}
		} else {
			if (yych <= ' ') {
				if (yych <= 0x1F) goto yy41;
				goto yy59;
			} else {
				if (yych == '`') goto yy21;
				goto yy41;
			}
		}
	} else {
		if (yych <= 0xED) {
			if (yych <= 0xDF) {
				if (yych <= 0xC1) goto yy21;
				goto yy45;
			} else {
				if (yych <= 0xE0) goto yy46;
				if (yych <= 0xEC) goto yy47;
				goto yy48;
			}
		} else {
			if (yych <= 0xF0) {
				if (yych <= 0xEF) goto yy47;
				goto yy49;
			} else {
				if (yych <= 0xF3) goto yy50;
				if (yych <= 0xF4) goto yy51;
				goto yy21;
			}
		}
	}
yy57:
	++p;
	p = marker;
	{ return (cmark_bufsize_t)(p - start); }
yy59:
	++p;
	yych = *p;
	if (yybm[0+yych] & 128) {
		goto yy55;
	}
	if (yych <= '`') {
		if (yych <= '\r') {
			if (yych <= 0x08) {
				if (yych <= 0x00) goto yy21;
				goto yy41;
			} else {
				if (yych <= '\n') goto yy57;
				if (yych <= '\f') goto yy41;
				goto yy57;
			}
		} else {
			if (yych <= ',') {
				if (yych == ' ') goto yy59;
				goto yy41;
			} else {
				if (yych <= '-') goto yy52;
				if (yych <= '_') goto yy41;
				goto yy21;
			}
		}
	} else {
		if (yych <= 0xEC) {
			if (yych <= 0xC1) {
				if (yych <= 0x7F) goto yy41;
				goto yy21;
			} else {
				if (yych <= 0xDF) goto yy45;
				if (yych <= 0xE0) goto yy46;
				goto yy47;
			}
		} else {
			if (yych <= 0xF0) {
				if (yych <= 0xED) goto yy48;
				if (yych <= 0xEF) goto yy47;
				goto yy49;
			} else {
				if (yych <= 0xF3) goto yy50;
				if (yych <= 0xF4) goto yy51;
				goto yy21;
			}
		}
	}
}

}

// Scan a closing gtk-doc code block.
cmark_bufsize_t _scan_close_gtkdoc_code_block(const unsigned char *p)
{
  const unsigned char *marker = NULL;
  const unsigned char *start = p;

{
	unsigned char yych;
	yych = *(marker = p);
	if (yych <= 0xDF) {
		if (yych <= '\\') {
			if (yych != '\n') goto yy64;
		} else {
			if (yych <= ']') goto yy65;
			if (yych <= 0x7F) goto yy64;
			if (yych >= 0xC2) goto yy66;
		}
	} else {
		if (yych <= 0xEF) {
			if (yych <= 0xE0) goto yy68;
			if (yych == 0xED) goto yy70;
			goto yy69;
		} else {
			if (yych <= 0xF0) goto yy71;
			if (yych <= 0xF3) goto yy72;
			if (yych <= 0xF4) goto yy73;
		}
	}
yy63:
	{ return 0; }
yy64:
	yych = *++p;
	goto yy63;
yy65:
	yych = *++p;
	if (yych == '|') goto yy74;
	goto yy63;
yy66:
	yych = *++p;
	if (yych <= 0x7F) goto yy67;
	if (yych <= 0xBF) goto yy64;
yy67:
	p = marker;
	goto yy63;
yy68:
	yych = *++p;
	if (yych <= 0x9F) goto yy67;
	if (yych <= 0xBF) goto yy66;
	goto yy67;
yy69:
	yych = *++p;
	if (yych <= 0x7F) goto yy67;
	if (yych <= 0xBF) goto yy66;
	goto yy67;
yy70:
	yych = *++p;
	if (yych <= 0x7F) goto yy67;
	if (yych <= 0x9F) goto yy66;
	goto yy67;
yy71:
	yych = *++p;
	if (yych <= 0x8F) goto yy67;
	if (yych <= 0xBF) goto yy69;
	goto yy67;
yy72:
	yych = *++p;
	if (yych <= 0x7F) goto yy67;
	if (yych <= 0xBF) goto yy69;
	goto yy67;
yy73:
	yych = *++p;
	if (yych <= 0x7F) goto yy67;
	if (yych <= 0x8F) goto yy69;
	goto yy67;
yy74:
	++p;
	{ return (cmark_bufsize_t)(p - start); }
}

}
