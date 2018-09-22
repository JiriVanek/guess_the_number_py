import nixio
import numpy as np
import os
import brainvision_parser as bvp

cwd = os.getcwd()
main_path = cwd + "/data/odml_nix_data/"
header_name = main_path + "P3Numbers_20150618_f_10_001.vhdr"

header, markers, eeg_data = bvp.read_brainvis_triplet(header_name)

chan_num = len(header["chan_lab"])

rs_eeg_data = np.reshape(eeg_data, [chan_num, int(np.size(eeg_data)/chan_num)])

# nix_filename = main_path + "metadata_conv.nix"
# nix_file = nixio.File.open(nix_filename)
# switch when done
nix_filename = main_path + "bla.nix"
data_units = "mV"
data_label = "voltage"
stepsize=header["sample_rate"]
with nixio.File.open(nix_filename, mode=nixio.FileMode.ReadWrite, compression=nixio.Compression.DeflateNormal) as nix_file:
  main_block_name = "something"
  b = nix_file.create_block(main_block_name, "eeg/main")
  eeg_g = b.create_group("rawdata", "eeg/channel")
  i = 0

  for rawda in rs_eeg_data:
    da = b.create_data_array(name=header["chan_lab"][i], array_type="eeg/channel", dtype=np.float32, data=rs_eeg_data[i])
    da.unit = data_units
    da.label = data_label
    # add a descriptor for the xaxis
    dim = da.append_sampled_dimension(stepsize)
    dim.unit = "s"
    dim.label = "time"
    dim.offset = 0.0  # optional
    eeg_g.data_arrays.append(da)
    i = i + 1

  stimuli_g = b.create_group("stimuli", "eeg/stimuli")

  da_stname = b.create_data_array(name="stimuli", array_type="stimuli/id", dtype=np.int, data=markers[0])
  da_stname.label="Stimulus id"
  da_sttime = b.create_data_array(name="stimuli_time", array_type="stimuli/time", dtype=np.int, data=markers[1])
  da_sttime.label="stimulus time points"
  stimuli_g.data_arrays.extend([da_stname, da_sttime])

  mtag = b.create_multi_tag("stimtochannel", "stimulus.times", da_sttime)
  mtag.create_feature(da_stname, nixio.LinkType.Indexed)

  for da in eeg_g.data_arrays:
    mtag.references.append(da)
