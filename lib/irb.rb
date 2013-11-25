require 'ripl'
require_relative 'monastery.rb'

include Templates
include Properties

w = Water.create
k = TeaKettle.create
p = Poison.create
p.make Small
w.move(k.hollow)
p.move(k.hollow)
p k.hollow.contents

def testSize
    t1 = Thing.new
    t2 = Thing.new
    t1.make Big
    t2.make Small
    p t1.size > t2.size
end

testSize

Ripl.start :binding => binding
