require 'ripl'
require_relative 'monastery.rb'

include Templates
include Properties

w = Water.create
k = TeaKettle.create
p = Poison.create
p.make Small
#w.move(k.hollow)
p.move(k.hollow)
p k.hollow.contents

Ripl.start :binding => binding
