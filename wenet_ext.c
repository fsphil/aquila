
#define PY_SSIZE_T_CLEAN
#include <Python.h>

static uint16_t _crc16(const uint8_t *data, size_t length)
{
	uint16_t x, crc = 0xFFFF;
	
	while(length--)
	{
		x  = crc >> 8 ^ *data++;
		x ^= x >> 4;
		
		crc = (crc << 8) ^ (x << 12) ^ (x << 5) ^ x;
	}
	
	return(crc);
}

static PyObject *wenet_ext_crc16(PyObject *self, PyObject *args)
{
	const uint8_t *data;
	uint16_t crc;
	Py_ssize_t count;
	
	if(!PyArg_ParseTuple(args, "y#", &data, &count))
	{
		return(NULL);
	}
	
	crc = _crc16(data, count);
	
	return(Py_BuildValue("H", crc));
}

/* LDPC Encoder, using a 'RA' encoder written by Bill Cowley VK5DSP in March 2016. */

#define NIBITS 2064
#define NPBITS  516
#define NWT      12

#define NIBYTES ((int) (NIBITS + 7) / 8)
#define NPBYTES ((int) (NPBITS + 7) / 8)

#include "hrow2064.h"

static void _ldpc_encode(const uint8_t ibytes[NIBYTES], uint8_t pbytes[NPBYTES])
{
	unsigned int p, i, tmp;
	unsigned par = 0;
	
	memset(pbytes, 0, NPBYTES);
	
	for(p = 0; p < NPBITS; p++)
	{
		for(i = 0; i < NWT; i++)
		{
			tmp  = _hrows[p * NWT + i];
			par += ibytes[tmp / 8] >> (7 - (tmp & 7));
		}
		
		par &= 1;
		
		pbytes[p / 8] |= par << (7 - (p & 7));
	}
}

static PyObject *wenet_ext_ldpc_encode(PyObject *self, PyObject *args)
{
	const uint8_t *ibytes;
	uint8_t pbytes[NPBYTES];
	Py_ssize_t count;
	
	if(!PyArg_ParseTuple(args, "y#", &ibytes, &count))
	{
		return(NULL);
	}
	
	if(count != NIBYTES)
	{
		PyErr_Format(PyExc_ValueError, "Buffer length must be exactly %d bytes.", NIBYTES);
		return(NULL);
	}
	
	_ldpc_encode(ibytes, pbytes);
	
	return(Py_BuildValue("y#", pbytes, NPBYTES));
}

static PyObject *wenet_ext_reverse_bits(PyObject *self, PyObject *args)
{
	const uint8_t *data;
	Py_ssize_t count;
	uint8_t *rdata;
	PyObject *result;
	int i;
	
	if(!PyArg_ParseTuple(args, "y#", &data, &count))
	{
		return(NULL);
	}
	
	rdata = malloc(count);
	if(!rdata)
	{
		PyErr_SetString(PyExc_MemoryError, "Out of memory.");
		return(NULL);
	}
	
	for(i = 0; i < count; i++)
	{
		rdata[i] =
			((data[i] & 0x80) >> 7) |
			((data[i] & 0x40) >> 5) |
			((data[i] & 0x20) >> 3) |
			((data[i] & 0x10) >> 1) |
			((data[i] & 0x08) << 1) |
			((data[i] & 0x04) << 3) |
			((data[i] & 0x02) << 5) |
			((data[i] & 0x01) << 7);
	}
	
	result = Py_BuildValue("y#", rdata, count);
	free(rdata);
	
	return(result);
}

static PyMethodDef wenet_ext_methods[] = {
	{ "crc16", wenet_ext_crc16, METH_VARARGS, "Encode CRC16 word." },
	{ "ldpc_encode", wenet_ext_ldpc_encode, METH_VARARGS, "Encode LDPC parity bits." },
	{ "reverse_bits", wenet_ext_reverse_bits, METH_VARARGS, "Reverse the bit order in a byte array." },
	{ NULL, NULL, 0, NULL }
};

static struct PyModuleDef wenet_ext_module = {
	PyModuleDef_HEAD_INIT,
	"wenet_ext",
	"Python extensions for wenet.",
	-1,
	wenet_ext_methods
};

PyMODINIT_FUNC PyInit_wenet_ext(void)
{
	return(PyModule_Create(&wenet_ext_module));
}

