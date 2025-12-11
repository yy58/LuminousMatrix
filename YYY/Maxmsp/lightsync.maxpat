{
	"patcher" : 	{
		"fileversion" : 1,
		"appversion" : 		{
			"major" : 9,
			"minor" : 0,
			"revision" : 9,
			"architecture" : "x64",
			"modernui" : 1
		}
,
		"classnamespace" : "box",
		"rect" : [ 263.0, 127.0, 1000.0, 703.0 ],
		"gridsize" : [ 15.0, 15.0 ],
		"boxes" : [ 			{
				"box" : 				{
					"id" : "obj-1",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 276.829274892807007, 143.902442455291748, 120.0, 22.0 ],
					"text" : "udpreceive 8000"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-2",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "", "" ],
					"patching_rect" : [ 276.829274892807007, 182.926833629608154, 120.0, 22.0 ],
					"text" : "route /light"
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-3",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 4,
					"outlettype" : [ "float", "float", "float", "float" ],
					"patching_rect" : [ 535.365866422653198, 330.487812757492065, 120.0, 22.0 ],
					"text" : "unpack f f f f"
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "disp-x",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 417.073180675506592, 223.170737028121948, 60.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "disp-y",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 486.58537745475769, 223.170737028121948, 60.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "disp-area",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 556.097574234008789, 223.170737028121948, 60.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"format" : 6,
					"id" : "disp-b",
					"maxclass" : "flonum",
					"numinlets" : 1,
					"numoutlets" : 2,
					"outlettype" : [ "", "bang" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 626.829283237457275, 223.170737028121948, 60.0, 22.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "scale-pitch",
					"maxclass" : "newobj",
					"numinlets" : 6,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 229.268298149108887, 398.780497312545776, 140.0, 22.0 ],
					"text" : "scale 0. 1. 36. 96."
				}

			}
, 			{
				"box" : 				{
					"id" : "mtof",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 324.390251636505127, 498.780499696731567, 60.0, 22.0 ],
					"text" : "mtof"
				}

			}
, 			{
				"box" : 				{
					"id" : "sigfreq",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 995.121974945068359, 392.682936191558838, 60.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "cycle",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 995.121974945068359, 437.804888486862183, 80.0, 22.0 ],
					"text" : "cycle~"
				}

			}
, 			{
				"box" : 				{
					"id" : "cycle2",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 324.390251636505127, 567.073184251785278, 80.0, 22.0 ],
					"text" : "cycle~"
				}

			}
, 			{
				"box" : 				{
					"id" : "scale-cut",
					"maxclass" : "newobj",
					"numinlets" : 6,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 395.121960639953613, 398.780497312545776, 140.0, 22.0 ],
					"text" : "scale 0. 1. 200. 5000."
				}

			}
, 			{
				"box" : 				{
					"id" : "lores",
					"maxclass" : "newobj",
					"numinlets" : 3,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1141.463441848754883, 437.804888486862183, 120.0, 22.0 ],
					"text" : "lores~ 0 0.7"
				}

			}
, 			{
				"box" : 				{
					"id" : "scale-amp",
					"maxclass" : "newobj",
					"numinlets" : 6,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 751.21953010559082, 398.780497312545776, 140.0, 22.0 ],
					"text" : "scale 0. 1. 0. 0.9"
				}

			}
, 			{
				"box" : 				{
					"id" : "line-amp",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 2,
					"outlettype" : [ "signal", "bang" ],
					"patching_rect" : [ 909.756119251251221, 517.073183059692383, 60.0, 22.0 ],
					"text" : "line~"
				}

			}
, 			{
				"box" : 				{
					"id" : "mult-amp",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 1008.536609411239624, 578.048794269561768, 60.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "harmony-gain-scale",
					"maxclass" : "newobj",
					"numinlets" : 6,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 535.365866422653198, 637.804893255233765, 140.0, 22.0 ],
					"text" : "scale 0. 1. 0. 0.7"
				}

			}
, 			{
				"box" : 				{
					"id" : "sig-harm",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 909.756119251251221, 578.048794269561768, 60.0, 22.0 ],
					"text" : "sig~"
				}

			}
, 			{
				"box" : 				{
					"id" : "harm-mul",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 962.195144891738892, 678.048796653747559, 60.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "area-delay-scale",
					"maxclass" : "newobj",
					"numinlets" : 6,
					"numoutlets" : 1,
					"outlettype" : [ "" ],
					"patching_rect" : [ 567.073184251785278, 398.780497312545776, 160.0, 22.0 ],
					"text" : "scale 0. 1. 50 800"
				}

			}
, 			{
				"box" : 				{
					"id" : "tapin",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "tapconnect" ],
					"patching_rect" : [ 665.853674411773682, 729.268310070037842, 100.0, 22.0 ],
					"text" : "tapin~ 2000"
				}

			}
, 			{
				"box" : 				{
					"id" : "tapout",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 851.219532489776611, 678.048796653747559, 100.0, 22.0 ],
					"text" : "tapout~"
				}

			}
, 			{
				"box" : 				{
					"id" : "delay-gain",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 863.414654731750488, 745.121968984603882, 60.0, 22.0 ],
					"text" : "*~"
				}

			}
, 			{
				"box" : 				{
					"id" : "sum",
					"maxclass" : "newobj",
					"numinlets" : 2,
					"numoutlets" : 1,
					"outlettype" : [ "signal" ],
					"patching_rect" : [ 962.195144891738892, 737.804895639419556, 60.0, 22.0 ],
					"text" : "+~"
				}

			}
, 			{
				"box" : 				{
					"id" : "ezdac",
					"maxclass" : "ezdac~",
					"numinlets" : 2,
					"numoutlets" : 0,
					"patching_rect" : [ 1030.487829446792603, 818.292702436447144, 50.0, 50.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "meter",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 1113.414660692214966, 781.707335710525513, 80.0, 50.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "toggle-dac",
					"maxclass" : "toggle",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "int" ],
					"parameter_enable" : 0,
					"patching_rect" : [ 1071.951245069503784, 781.707335710525513, 20.0, 20.0 ]
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "tapout", 0 ],
					"midpoints" : [ 576.573184251785278, 669.444071114063263, 860.719532489776611, 669.444071114063263 ],
					"source" : [ "area-delay-scale", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "lores", 0 ],
					"midpoints" : [ 1004.621974945068359, 470.185438871383667, 1069.418822526931763, 470.185438871383667, 1069.418822526931763, 428.185438871383667, 1150.963441848754883, 428.185438871383667 ],
					"source" : [ "cycle", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum", 0 ],
					"midpoints" : [ 872.914654731750488, 777.158376693725586, 922.077385902404785, 777.158376693725586, 922.077385902404785, 728.185454607009888, 971.695144891738892, 728.185454607009888 ],
					"source" : [ "delay-gain", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum", 0 ],
					"source" : [ "harm-mul", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sig-harm", 0 ],
					"midpoints" : [ 544.865866422653198, 610.702687621116638, 839.677431166172028, 610.702687621116638, 839.677431166172028, 568.702687621116638, 919.256119251251221, 568.702687621116638 ],
					"source" : [ "harmony-gain-scale", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mult-amp", 1 ],
					"midpoints" : [ 919.256119251251221, 559.341704607009888, 1059.036609411239624, 559.341704607009888 ],
					"source" : [ "line-amp", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mult-amp", 0 ],
					"midpoints" : [ 1150.963441848754883, 519.497954607009888, 1018.036609411239624, 519.497954607009888 ],
					"source" : [ "lores", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "cycle2", 0 ],
					"midpoints" : [ 333.890251636505127, 549.850091695785522, 333.890251636505127, 549.850091695785522 ],
					"order" : 2,
					"source" : [ "mtof", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "harm-mul", 0 ],
					"midpoints" : [ 333.890251636505127, 499.616475999355316, 971.695144891738892, 499.616475999355316 ],
					"order" : 1,
					"source" : [ "mtof", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sigfreq", 0 ],
					"midpoints" : [ 333.890251636505127, 430.530264377593994, 954.332609593868256, 430.530264377593994, 954.332609593868256, 388.530264377593994, 1004.621974945068359, 388.530264377593994 ],
					"order" : 0,
					"source" : [ "mtof", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "sum", 1 ],
					"midpoints" : [ 1018.036609411239624, 599.616481244564056, 1012.695144891738892, 599.616481244564056 ],
					"source" : [ "mult-amp", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-2", 0 ],
					"source" : [ "obj-1", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-3", 0 ],
					"midpoints" : [ 286.329274892807007, 267.757731974124908, 544.865866422653198, 267.757731974124908 ],
					"source" : [ "obj-2", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "area-delay-scale", 0 ],
					"midpoints" : [ 612.199199755986569, 375.6779865026474, 576.573184251785278, 375.6779865026474 ],
					"order" : 0,
					"source" : [ "obj-3", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "disp-area", 0 ],
					"midpoints" : [ 612.199199755986569, 362.233018398284912, 588.830804328123691, 362.233018398284912, 588.830804328123691, 212.937620043754578, 565.597574234008789, 212.937620043754578 ],
					"order" : 1,
					"source" : [ "obj-3", 2 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "disp-b", 0 ],
					"midpoints" : [ 645.865866422653198, 362.233018398284912, 640.577932596206665, 362.233018398284912, 640.577932596206665, 212.937620043754578, 636.329283237457275, 212.937620043754578 ],
					"order" : 1,
					"source" : [ "obj-3", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "disp-x", 0 ],
					"midpoints" : [ 544.865866422653198, 362.233018398284912, 485.336547791957855, 362.233018398284912, 485.336547791957855, 212.937620043754578, 426.573180675506592, 212.937620043754578 ],
					"order" : 0,
					"source" : [ "obj-3", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "disp-y", 0 ],
					"midpoints" : [ 578.532533089319827, 362.233018398284912, 537.08367606004083, 362.233018398284912, 537.08367606004083, 212.937620043754578, 496.08537745475769, 212.937620043754578 ],
					"order" : 0,
					"source" : [ "obj-3", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "scale-amp", 0 ],
					"midpoints" : [ 645.865866422653198, 382.277793049812317, 760.71953010559082, 382.277793049812317 ],
					"order" : 0,
					"source" : [ "obj-3", 3 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "scale-cut", 0 ],
					"midpoints" : [ 578.532533089319827, 378.546449899673462, 404.621960639953613, 378.546449899673462 ],
					"order" : 1,
					"source" : [ "obj-3", 1 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "scale-pitch", 0 ],
					"midpoints" : [ 544.865866422653198, 364.367345929145813, 238.768298149108887, 364.367345929145813 ],
					"order" : 1,
					"source" : [ "obj-3", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "line-amp", 0 ],
					"midpoints" : [ 760.71953010559082, 550.357856869697571, 839.677431166172028, 550.357856869697571, 839.677431166172028, 508.357856869697571, 919.256119251251221, 508.357856869697571 ],
					"source" : [ "scale-amp", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "lores", 1 ],
					"midpoints" : [ 404.621960639953613, 490.013026118278503, 980.013644099235535, 490.013026118278503, 980.013644099235535, 428.185438871383667, 1201.463441848754883, 428.185438871383667 ],
					"source" : [ "scale-cut", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "mtof", 0 ],
					"midpoints" : [ 238.768298149108887, 460.006341695785522, 333.890251636505127, 460.006341695785522 ],
					"source" : [ "scale-pitch", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "harm-mul", 1 ],
					"midpoints" : [ 919.256119251251221, 639.810454607009888, 1012.695144891738892, 639.810454607009888 ],
					"source" : [ "sig-harm", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "cycle", 0 ],
					"source" : [ "sigfreq", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ezdac", 1 ],
					"midpoints" : [ 971.695144891738892, 789.239078521728516, 1070.987829446792603, 789.239078521728516 ],
					"order" : 1,
					"source" : [ "sum", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ezdac", 0 ],
					"midpoints" : [ 971.695144891738892, 789.239078521728516, 1039.987829446792603, 789.239078521728516 ],
					"order" : 2,
					"source" : [ "sum", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "meter", 0 ],
					"midpoints" : [ 971.695144891738892, 771.328631401062012, 1122.914660692214966, 771.328631401062012 ],
					"order" : 0,
					"source" : [ "sum", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "delay-gain", 0 ],
					"midpoints" : [ 860.719532489776611, 722.984415650367737, 872.914654731750488, 722.984415650367737 ],
					"source" : [ "tapout", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "ezdac", 0 ],
					"midpoints" : [ 1081.451245069503784, 810.38225531578064, 1039.987829446792603, 810.38225531578064 ],
					"source" : [ "toggle-dac", 0 ]
				}

			}
 ],
		"dependency_cache" : [  ],
		"autosave" : 0
	}

}
