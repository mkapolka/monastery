module Properties
	class Fuzzy < Property
		description "is fuzzy"
		types :physical
	end

   class Boilable < Property
      description "can be boiled"
      types :physical
      revealed_by :chem_knowledge

      upon :tick do |me|
         if me.hot?
            me.make :boiling
         end
      end
   end

   class Boiling < Property
      description "is boiling"
      types :physical
      revealed_by :look

      upon :tick do |me|
         if rand() < 0.1
            me.destroy
         end
      end
   end

	class Hard < Property
		 description "is hard"
		 types :physical
		 revealed_by :feel

		 upon :make do |me|
			 me.say "#{me.name} becomes hard.", :see
		 end

		 upon :bash do |me, basher|
				puts "#{me.name} rings like a gong!"
		 end
	end

   class Soft < Property
      description "is soft"
      types :physical
      revealed_by :feel

      upon :make do |me|
         me.say "#{me.name} becomes soft.", :see
      end
   end

	class Hot < Property
		description "is hot"
		types :physical
		revealed_by :feel, :look

		upon :make do |me|
			me.say "#{me.name} becomes hot.", :see
		end

		upon :unmake do |me|
			me.say "#{me.name} cools down.", :see
		end

		upon :tick do |me|
			if rand < 0.1
				me.unmake :hot
			end
		end
	end

	class Size < Property
		attr_accessor :value;

		def initialize
			super;
			@value = 0;
		end

		def describe()
			return "" if not @value === [0...5]
			"is " + [
				"tiny",
				"small",
				"medium-sized",
				"big",
				"huge"
			][value]
		end

		def make(me)
			me.properties[:size] = self;
			me.prop_accessor(:size);
		end

		def +(value)
			value + value;
		end

		def >(other)
			return value > other.value if other.respond_to? value;
			return true;
		end

		def <(other)
			return value < other.value if other.respond_to? value;
			return true;
		end
	end

	 #Helps create new sizes
	 def self.make_size(name, v)
      cnew = Class.new(Size);
      cnew.class_eval do
				@@default_value = v;
				def self.new
					out = Size.new;
					out.value = @@default_value;
					return out;
				end
			end
      Properties.const_set(name.to_s.capitalize, cnew)
	 end

	["Tiny","Small","Medium","Big","Huge"].each_with_index do |v,i|
		make_size(v,i);
	end

	class Bumpy < Property
		description "is bumpy"
	end


	class Open < Property
		description  "is open";

		upon :jostle do |me, jostler|
			next if not me.container?
			me.contents.each do |x|
				x.remove_from_container
			end
		end
	end

	class Openable < Property
		description "can be opened"

      upon :make do |me|
         me.metaclass.class_eval do
            define_method(:open) do
               me.make :open
            end

            define_method(:close) do
               me.unmake :open
            end
         end
      end


		#action "Open" do |me, actor|
			##move_nearby :actor
			#me.make :open
		#end

		#action "Close" do |me, actor|
			##move_nearby :actor
			#me.make :close	
		#end
	end
end

