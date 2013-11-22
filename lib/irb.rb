require 'irb'
require_relative 'monastery.rb'

include Templates
include Properties

w = Water.create
k = TeaKettle.create
p = Poison.create
w.move(k.hollow)
p.move(k.hollow)
p k.hollow.contents

IRB.start(__FILE__)
