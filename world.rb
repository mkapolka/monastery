module The_World
	class World
		attr_accessor :things

		def initialize(*templates)
			self.things ||= [];

			templates.each do |x|
				self.things << Nouns::spawn(x)
			end
		end

		def tick
			self.things.each do |x|
				x.do :tick
			end
		end
	end
end
