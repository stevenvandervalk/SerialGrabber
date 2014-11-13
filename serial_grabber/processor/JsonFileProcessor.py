# !/usr/bin/env python
# SerialGrabber reads data from a serial port and processes it with the
# configured processor.
# Copyright (C) 2012  NigelB
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
import json
from time import localtime, strftime

import logging
import shutil
import tempfile
from serial_grabber.processor import TransactionFilteringProcessor
from serial_grabber import thingspeak

import os, os.path


class JsonFileProcessor(TransactionFilteringProcessor):
    """
    Writes the last *limit* transactions that were not filtered out by *transaction_filter* as a JSON encoded array
    to *output_file*.

    :param str output_file: The filename of the json output file.
    :param transaction_filter: Used to filter transactions.
    :type transaction_filter: serial_grabber.filter.TransactionFilter or None
    :param int limit: The number of transactions keep and write to the output_file, -1 for unlimited.
    :param int permission: The file permissions to set on the output_file.

    """
    logger = logging.getLogger("JsonFileProcessor")

    def __init__(self, output_file, transaction_filter=None, limit=-1, permission=0644):
        self.setTransactionFilter(transaction_filter)
        self.limit = limit
        self.output_file = output_file
        self.permission = permission
        _dir = os.path.dirname(os.path.abspath(output_file))
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        self.data = []
        if os.path.exists(self.output_file):
            with open(self.output_file, "rb") as existing:
                data = json.load(existing)
            for i in data:
                self.data.append(json.dumps(i))

    def process(self, process_entry):
        filtered = False
        if self.filter:
            filtered = self.filter.filter(process_entry)
        self.logger.debug("Filtered: %s, %s" % (filtered, self.output_file))
        try:
            if not filtered:
                if self.limit > 0 and len(self.data) >= self.limit:
                    self.data = self.data[((self.limit - 1 ) * -1):]
                    if (self.limit - 1) == 0:
                        self.data = []


                #print out state of data to see if motion detection written

                print ', '.join(map(str, self.data))

                print str(self.data).strip('[]')



                # remove motion detecting observation
                # data.pop()



                # set the content of what is written

                def write_to_thingspeak(channel):


                    field_1 = self.data[0]
                    field_2 = self.data[1]
                    field_3 = self.data[2]
                    field_4 = self.data[3]
                    field_5 = self.data[4]
                    field_6 = self.data[5]

                    try:
                        response = channel.update([field_1,field_2,field_3,field_4,field_5,field_6])

                        print strftime("%a, %d %b %Y %H:%M:%S", localtime())
                        print response.status, response.reason
                        thingspeak_response = response.read()
                    except:
                        print "connection failed"




                # write data object to channel


                channel = thingspeak.channel('YOURKEYHERE')

                #while True:
                write_to_thingspeak(channel)
                #sleep for 16 seconds (api limit of 15 secs)
                #sleep(16)




                self.data.append(json.dumps(process_entry.data.payload.config_delegate))
                fid, path = tempfile.mkstemp()
                with os.fdopen(fid, "wb") as out_data:
                    out_data.write("[")
                    out_data.write(",".join(self.data))
                    out_data.write("]")
                os.chmod(path, self.permission)
                shutil.move(path, self.output_file)
                return True
        except:
            import traceback

            traceback.print_exc()
            return False






