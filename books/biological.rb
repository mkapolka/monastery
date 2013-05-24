################################################################################
#                                                                              #
# Sister Gerstie's Big Book of Biology.                                        #
#                                                                              #
################################################################################

module Properties
	the_following_are :biological do
      class Oxygen_Carrier < Property
         description "carries oxygen"
      end

      class Oxygenated < Property
         description "is rich with oxygen"
         upon "tick" do |me|
            me.unmake :oxygenated if rand < 0.1;
         end
      end

      class Needs_Oxygen < Property
         description "needs oxygen to live"
         upon "tick" do |me|
            next if me.oxygenated?;
            me.unmake :alive if rand < 0.1;
         end
      end

      class Blood_Pumping < Property
         description "supplies oxygen to other organs"
         types :cardiovascular
         upon "tick" do |me|
            #require me.alive?
            #if me.touching.contains_one_with_adj :oxygen_carrier
            # me.touching.each do |other| do
            #  other.do :heartbeat other, me
            # end
            #end
         end
      end

      class Alive < Property
         description "is alive"
         upon "tick" do |me|
            puts "#{me.name} ages!"
         end
      end

      class Mobile < Property
         description "is mobile"
      end
	end
end

class Noun
   def skeletally(*params)
      params.each do |param|
         is param;
         self.get_property(param).types << :skeletal
      end
   end
end

###################################
###### APPENDIX              ######
###################################
module Forms
	form :heart do
		name "a heart"
		is :blood_pumping
      lends_properties :cardiovascular
	end

   form :brain do
      name "a brain"
      lends_properties :psychological
   end

   form :stomach do
      name "a stomach"
      lends_properties :gastrointestinal
   end

	form :blood do
		name "some blood"
		is :oxygen_carrier
	end

   form :skeleton do
      name "a skeleton"
      skeletally :mobile
      lends_properties :skeletal
   end
end
