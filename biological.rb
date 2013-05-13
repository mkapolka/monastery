###################################
######THE BIG BOOK OF BIOLOGY######
###################################

module Properties
	the_following_are :biological do
		the_following_are :cardiovascular do

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

		end
	end
end

###################################
###### APPENDIX              ######
###################################
module Nouns
	noun :heart do
		name "a heart"
		is :blood_pumping
	end

	noun :blood do
		name "some blood"
		is :oxygen_carrier
	end
end
